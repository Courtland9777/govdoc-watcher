from govdoc_watcher.config import SourceConfig
from govdoc_watcher.discovery import extract_candidates
from govdoc_watcher.ranking import pick_best


def mk_src():
    return SourceConfig('cms-icd10-pcs-guidelines', 'CMS', 'CMS', 'https://x', 'ICD', ["official", "icd-10-pcs", "coding guidelines"], ["not yet available"], ["pdf"], True, None, True)


def test_rejects_annual_file():
    html = '''<a href="/files/document/2026-official-icd-10-pcs-coding-guidelines.pdf">2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None


def test_latest_dated_update_outranks_older_year():
    html = '''<a href="/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf">April 1, 2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/january-15-2027-official-icd-10-pcs-coding-guidelines.pdf">January 15, 2027 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert 'january-15-2027' in best.url


def test_later_dated_update_outranks_earlier_same_year():
    html = '''<a href="/files/document/january-15-2027-official-icd-10-pcs-coding-guidelines.pdf">January 15, 2027 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/october-1-2027-official-icd-10-pcs-coding-guidelines.pdf">October 1, 2027 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert 'october-1-2027' in best.url


def test_unavailable_never_selected():
    html = '''<a href="/files/document/april-1-2025-official-icd-10-pcs-coding-guidelines.pdf">2025 Official ICD-10-PCS Coding Guidelines (PDF) - NOT YET AVAILABLE</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None


def test_excludes_cm_guidelines_pdf():
    html = '''<a href="/files/document/2026-official-icd-10-cm-coding-guidelines.pdf">2026 Official ICD-10-CM Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None


def test_excludes_zip_files():
    html = '''<a href="/files/zip/april-1-2026-official-icd-10-pcs-coding-guidelines.zip">April 1, 2026 Official ICD-10-PCS Coding Guidelines (ZIP)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert best is None
