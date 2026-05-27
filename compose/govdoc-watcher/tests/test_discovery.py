from govdoc_watcher.discovery import extract_candidates


def test_extract_candidates_cms_style():
    html = '''<a href="/files/document/april-1-2026-official-icd-10-pcs-coding-guidelines.pdf">April 1, 2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/2026-official-icd-10-pcs-coding-guidelines.pdf">2026 Official ICD-10-PCS Coding Guidelines (PDF)</a>
    <a href="/files/document/2025-official-icd-10-pcs-coding-guidelines.pdf">2025 Official ICD-10-PCS Coding Guidelines (PDF)</a>'''
    c = extract_candidates(html, 'https://www.cms.gov/medicare/coding-billing/icd-10-codes')
    assert len(c) == 3
    assert c[0].url.startswith('https://www.cms.gov/files/document/')
