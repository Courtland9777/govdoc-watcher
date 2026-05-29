from dataclasses import dataclass
from pathlib import Path
import re
import yaml


@dataclass
class SourceConfig:
    id: str
    name: str
    agency: str
    discovery_url: str
    document_type: str
    required_text_patterns: list[str]
    exclude_text_patterns: list[str]
    allowed_extensions: list[str]
    prefer_newest_year: bool
    check_interval_hours: int | None
    enabled: bool


def _is_valid_source_id(value: str) -> bool:
    return bool(re.fullmatch(r"[a-z0-9-]+", value))


def load_sources(path: Path) -> list[SourceConfig]:
    if not path.exists():
        raise ValueError(f"Missing source config: {path}")
    data = yaml.safe_load(path.read_text())
    if not isinstance(data, dict) or "sources" not in data:
        raise ValueError("Config must include top-level 'sources' list")
    out = []
    seen = set()
    for item in data["sources"]:
        merged = {
            "allowed_extensions": ["pdf"],
            "prefer_newest_year": True,
            "check_interval_hours": None,
        }
        merged.update(item)
        src = SourceConfig(**merged)
        if src.id in seen:
            raise ValueError(f"Duplicate source id: {src.id}")
        seen.add(src.id)
        if not _is_valid_source_id(src.id):
            raise ValueError(f"Invalid source id: {src.id}")
        out.append(src)
    return out
