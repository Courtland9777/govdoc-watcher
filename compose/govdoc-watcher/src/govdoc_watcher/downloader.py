from pathlib import Path
import httpx


def download_to_temp(url: str, timeout: int, user_agent: str) -> tuple[Path, dict]:
    tmp = Path('/tmp/govdoc-download.pdf.tmp')
    headers = {"User-Agent": user_agent}
    with httpx.stream("GET", url, headers=headers, timeout=timeout, follow_redirects=True) as r:
        r.raise_for_status()
        with tmp.open('wb') as f:
            for chunk in r.iter_bytes():
                f.write(chunk)
        meta = {"etag": r.headers.get("etag"), "last_modified": r.headers.get("last-modified"), "content_type": r.headers.get("content-type")}
    return tmp, meta
