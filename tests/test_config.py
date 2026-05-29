from pathlib import Path
from govdoc_watcher.config import load_sources


def test_load_sources(tmp_path: Path):
    f = tmp_path / 's.yaml'
    f.write_text('sources:\n  - id: a-1\n    name: n\n    agency: a\n    discovery_url: https://x\n    document_type: d\n    required_text_patterns: [official]\n    exclude_text_patterns: [no]\n    allowed_extensions: [pdf]\n    prefer_newest_year: true\n    enabled: true\n')
    s = load_sources(f)
    assert len(s) == 1
