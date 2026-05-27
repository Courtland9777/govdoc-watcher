from pathlib import Path
import tempfile
import httpx


def download_to_temp(url: str, timeout: int, user_agent: str) -> tuple[Path, dict]:
    headers = {"User-Agent": user_agent}
    with tempfile.NamedTemporaryFile(prefix="govdoc-download-", suffix=".pdf", delete=False) as tf:
        tmp = Path(tf.name)

    try:
        with httpx.stream("GET", url, headers=headers, timeout=timeout, follow_redirects=True) as r:
            r.raise_for_status()
            with tmp.open("wb") as f:
                for chunk in r.iter_bytes():
                    f.write(chunk)
            meta = {
                "etag": r.headers.get("etag"),
                "last_modified": r.headers.get("last-modified"),
                "content_type": r.headers.get("content-type"),
            }
    except Exception:
        if tmp.exists():
            tmp.unlink()
        raise

    return tmp, meta
