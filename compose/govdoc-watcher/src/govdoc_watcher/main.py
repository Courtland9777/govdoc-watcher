import logging
import os
import time
from pathlib import Path
import httpx

from govdoc_watcher.config import load_sources
from govdoc_watcher.discovery import extract_candidates
from govdoc_watcher.ranking import pick_best
from govdoc_watcher.storage import ensure_dirs, sha256_file, promote_pdf
from govdoc_watcher.downloader import download_to_temp
from govdoc_watcher.metadata import load_metadata, save_metadata, utc_now
from govdoc_watcher.logging_config import configure_logging


def process_source(src, timeout, user_agent):
    log = logging.getLogger('govdoc')
    md = load_metadata(src.id)
    md["last_checked_timestamp"] = utc_now()
    try:
        r = httpx.get(src.discovery_url, timeout=timeout, follow_redirects=True, headers={"User-Agent": user_agent})
        r.raise_for_status()
        candidates = extract_candidates(r.text, src.discovery_url)
        best, score, reason = pick_best(src, candidates)
        md["candidate_count_found"] = len(candidates)
        md["last_discovery_success_timestamp"] = utc_now()
        if not best:
            md["last_status"] = "no_valid_candidate"
            save_metadata(src.id, md)
            return
        tmp, hmeta = download_to_temp(best.url, timeout, user_agent)
        if tmp.stat().st_size == 0 or not tmp.read_bytes().startswith(b"%PDF-"):
            tmp.unlink(missing_ok=True)
            md["last_status"] = "validation_failed"
            save_metadata(src.id, md)
            return
        new_sha = sha256_file(tmp)
        if md.get("current_sha256") == new_sha:
            tmp.unlink(missing_ok=True)
            md["last_status"] = "unchanged"
            save_metadata(src.id, md)
            return
        archived, active = promote_pdf(src.id, tmp, new_sha)
        old_sha = md.get("current_sha256")
        md.update({
            "source_id": src.id, "source_name": src.name, "agency": src.agency, "discovery_url": src.discovery_url,
            "selected_document_url": best.url, "selected_link_text": best.link_text,
            "selected_effective_year": best.year, "selected_effective_date": "April 1" if best.is_april_1 else None,
            "current_active_filename": active, "previous_sha256": old_sha, "current_sha256": new_sha,
            "etag": hmeta.get("etag"), "last_modified": hmeta.get("last_modified"), "last_status": "changed",
            "last_changed_timestamp": utc_now(), "last_successful_download_timestamp": utc_now(),
            "selected_candidate_ranking": {"score": score, "reason": reason}, "archived_previous_file": archived,
        })
        md.setdefault("first_seen_timestamp", utc_now())
        save_metadata(src.id, md)
        log.info("promotion success", extra={"source_id": src.id, "url": best.url, "sha256": new_sha})
    except Exception as e:
        md["error_count"] = int(md.get("error_count", 0)) + 1
        md["last_error_message"] = str(e)
        md["last_status"] = "error"
        save_metadata(src.id, md)


def main():
    run_once = os.getenv("RUN_ONCE", "false").lower() == "true"
    interval = int(os.getenv("DEFAULT_CHECK_INTERVAL_HOURS", "24"))
    timeout = int(os.getenv("HTTP_TIMEOUT_SECONDS", "30"))
    level = os.getenv("LOG_LEVEL", "INFO")
    user_agent = os.getenv("USER_AGENT", "govdoc-watcher/1.0")
    configure_logging(level)
    ensure_dirs()
    sources = [s for s in load_sources(Path('/app/config/sources.yaml')) if s.enabled]
    while True:
        for src in sources:
            process_source(src, timeout, user_agent)
        if run_once:
            break
        time.sleep(interval * 3600)


if __name__ == '__main__':
    main()
