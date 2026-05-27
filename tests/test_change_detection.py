from pathlib import Path


def test_pdf_validation_prefix(tmp_path: Path):
    good = tmp_path / 'a.pdf'
    bad = tmp_path / 'b.pdf'
    good.write_bytes(b'%PDF-1.4\nabc')
    bad.write_bytes(b'notpdf')
    assert good.read_bytes().startswith(b'%PDF-')
    assert not bad.read_bytes().startswith(b'%PDF-')
