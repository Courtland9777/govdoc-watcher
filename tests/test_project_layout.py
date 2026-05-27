from pathlib import Path


def test_root_layout_exists():
    required = [
        '.env.example', '.gitignore', 'Dockerfile', 'README.md', 'docker-compose.yaml', 'requirements.txt',
        'config', 'data', 'logs', 'src', 'tests'
    ]
    root = Path(__file__).resolve().parents[1]
    for item in required:
        assert (root / item).exists(), f"Missing required root item: {item}"
