from pathlib import Path

from govdoc_watcher.storage import promote_pdf, sha256_file


def test_sha256_file(tmp_path: Path):
    p = tmp_path / 'f.pdf'
    p.write_bytes(b'%PDF-1.7\nabc')
    assert len(sha256_file(p)) == 64


def test_promote_pdf_archives_using_old_active_hash(monkeypatch, tmp_path: Path):
    active_dir = tmp_path / "data" / "active"
    archive_dir = tmp_path / "data" / "archive"
    source_id = "source-1"

    old_active = active_dir / f"{source_id}.pdf"
    old_active.parent.mkdir(parents=True, exist_ok=True)
    old_active.write_bytes(b"%PDF-1.7\nold")

    new_tmp = tmp_path / "new.pdf"
    new_tmp.write_bytes(b"%PDF-1.7\nnew")

    old_sha = sha256_file(old_active)
    new_sha = sha256_file(new_tmp)

    from govdoc_watcher import storage

    real_path = Path

    def fake_path(p: str):
        if p.startswith("/data/"):
            return real_path(tmp_path / p.lstrip("/"))
        if p == "/logs":
            return real_path(tmp_path / "logs")
        return real_path(p)

    monkeypatch.setattr(storage, "Path", fake_path)

    archived, active = promote_pdf(source_id, new_tmp, new_sha)

    assert archived is not None
    assert old_sha[:12] in archived
    assert new_sha[:12] not in archived
    assert Path(active).read_bytes() == b"%PDF-1.7\nnew"
    assert Path(archived).read_bytes() == b"%PDF-1.7\nold"
