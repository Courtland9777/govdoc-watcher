from dataclasses import dataclass
from urllib.parse import urljoin
from bs4 import BeautifulSoup
import re


@dataclass
class Candidate:
    url: str
    link_text: str
    extension: str
    year: int | None
    is_april_1: bool


def _detect_year(text: str) -> int | None:
    m = re.search(r"\b(20\d{2})\b", text)
    return int(m.group(1)) if m else None


def _is_april_1(text: str) -> bool:
    return bool(re.search(r"april\s+1[,\s-]+20\d{2}", text.lower()))


def extract_candidates(html: str, base_url: str) -> list[Candidate]:
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        text = " ".join(a.get_text(" ", strip=True).split())
        full_url = urljoin(base_url, href)
        combined = f"{text} {full_url}"
        year = _detect_year(combined)
        is_april_1 = _is_april_1(combined)
        ext = full_url.split("?")[0].split(".")[-1].lower() if "." in full_url else ""
        candidates.append(Candidate(full_url, text, ext, year, is_april_1))
    return candidates
