from pathlib import Path
from datetime import datetime, timezone
import hashlib
import shutil


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()


def ensure_dirs() -> None:
    for p in [Path('/data/active'), Path('/data/archive'), Path('/data/metadata'), Path('/logs')]:
        p.mkdir(parents=True, exist_ok=True)


def promote_pdf(source_id: str, tmp_file: Path, new_sha: str) -> tuple[str | None, str]:
    active = Path(f"/data/active/{source_id}.pdf")
    archive_dir = Path(f"/data/archive/{source_id}")
    archive_dir.mkdir(parents=True, exist_ok=True)
    archived = None
    if active.exists():
        old_sha = sha256_file(active)
        stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
        archived = str(archive_dir / f"{stamp}-{old_sha[:12]}.pdf")
        shutil.move(str(active), archived)
    tmp_file.replace(active)
    return archived, str(active)
