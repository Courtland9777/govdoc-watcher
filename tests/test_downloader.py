from pathlib import Path

import pytest

from govdoc_watcher.downloader import download_to_temp


def test_download_to_temp_cleans_up_temp_file_on_stream_failure(monkeypatch):
    created: list[Path] = []

    class FakeResponse:
        headers = {"etag": "x", "last-modified": "y", "content-type": "application/pdf"}

        def __enter__(self):
            return self

        def __exit__(self, exc_type, exc, tb):
            return False

        def raise_for_status(self):
            return None

        def iter_bytes(self):
            yield b"%PDF-1.7\n"
            raise RuntimeError("stream failed")

    def fake_stream(*args, **kwargs):
        return FakeResponse()

    monkeypatch.setattr("govdoc_watcher.downloader.httpx.stream", fake_stream)

    original_unlink = Path.unlink

    def tracking_unlink(self, *args, **kwargs):
        created.append(self)
        return original_unlink(self, *args, **kwargs)

    monkeypatch.setattr(Path, "unlink", tracking_unlink)

    with pytest.raises(RuntimeError, match="stream failed"):
        download_to_temp("https://example.com/file.pdf", timeout=30, user_agent="ua")

    assert len(created) == 1
    assert not created[0].exists()
