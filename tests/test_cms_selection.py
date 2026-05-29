from pathlib import Path

from govdoc_watcher.config import SourceConfig
from govdoc_watcher.discovery import extract_candidates
from govdoc_watcher.main import process_source
from govdoc_watcher.ranking import pick_best


def mk_src():
    return SourceConfig(
        'cms-icd10-pcs-guidelines', 'CMS', 'CMS', 'https://www.cms.gov/medicare/coding-billing/icd-10-codes', 'ICD',
        ["official", "icd-10-pcs", "coding guidelines"], ["not yet available"], ["pdf"], True, None, True
    )


def test_rejects_annual_url():
    html = '<a href="/files/document/2025-official-icd-10-pcs-coding-guidelines.pdf">x</a>'
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None


def test_april_dated_update_url_match():
    html = '<a href="/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf">x</a>'
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is not None
    assert best.document_kind == 'dated_update'
    assert best.year == 2026
    assert best.effective_month == 'april'
    assert best.effective_day == 1


def test_non_april_dated_update_url_match():
    html = '<a href="/files/document/january-15-2027-official-icd-10-pcs-coding-guidelines.pdf">x</a>'
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is not None
    assert best.document_kind == 'dated_update'
    assert best.year == 2027
    assert best.effective_month == 'january'
    assert best.effective_day == 15


def test_rejects_impossible_day():
    html = '<a href="/files/document/april-32-2026-official-icd-10-pcs-coding-guidelines.pdf">x</a>'
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None


def test_unchanged_when_selected_url_matches_metadata_and_active_exists(monkeypatch, tmp_path: Path):
    from govdoc_watcher import main

    html = '<a href="/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf">April 1, 2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>'

    class Resp:
        text = html
        def raise_for_status(self):
            return None

    monkeypatch.setattr(main.httpx, 'get', lambda *args, **kwargs: Resp())

    saved = {}
    monkeypatch.setattr(main, 'load_metadata', lambda _sid: {
        'selected_document_url': 'https://www.cms.gov/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf'
    })
    monkeypatch.setattr(main, 'save_metadata', lambda sid, payload: saved.update({'sid': sid, 'payload': payload}))

    real_path = Path

    def fake_path(p: str):
        if p.startswith('/data/'):
            return real_path(tmp_path / p.lstrip('/'))
        return real_path(p)

    monkeypatch.setattr(main, 'Path', fake_path)

    active = tmp_path / 'data' / 'active' / 'cms-icd10-pcs-guidelines.pdf'
    active.parent.mkdir(parents=True, exist_ok=True)
    active.write_bytes(b'%PDF-1.7\nexisting')

    process_source(mk_src(), timeout=5, user_agent='test')

    assert saved['payload']['last_status'] == 'unchanged'
