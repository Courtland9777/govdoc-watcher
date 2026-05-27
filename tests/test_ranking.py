from govdoc_watcher.config import SourceConfig
from govdoc_watcher.discovery import extract_candidates
from govdoc_watcher.ranking import pick_best


def mk_src():
    return SourceConfig('cms-icd10-pcs-guidelines','CMS','CMS','https://x','ICD',["official","icd-10-pcs","coding guidelines"],["not yet available"],["pdf"],True,True,None,True)


def test_april_outranks_base_same_year():
    html = '''<a href="/files/document/2026-official-icd-10-pcs-coding-guidelines.pdf">2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf">April 1, 2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert 'april-1-2026' in best.url


def test_current_year_outranks_previous():
    html = '''<a href="/files/document/2025-official-icd-10-pcs-coding-guidelines.pdf">2025 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/2026-official-icd-10-pcs-coding-guidelines.pdf">2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    best, _, _ = pick_best(mk_src(), extract_candidates(html, 'https://www.cms.gov'))
    assert '2026' in best.url


def test_unavailable_never_selected():
    html = '''<a href="/files/document/2025-official-icd-10-pcs-coding-guidelines.pdf">2025 Official ICD-10-PCS Coding Guidelines (PDF) - NOT YET AVAILABLE</a>'''
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
