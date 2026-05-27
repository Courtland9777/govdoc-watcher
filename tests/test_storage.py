from pathlib import Path
from govdoc_watcher.storage import sha256_file


def test_sha256_file(tmp_path: Path):
    p = tmp_path / 'f.pdf'
    p.write_bytes(b'%PDF-1.7\nabc')
    assert len(sha256_file(p)) == 64
