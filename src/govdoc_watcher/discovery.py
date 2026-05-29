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
    document_kind: str | None = None
    effective_month: str | None = None
    effective_day: int | None = None
    effective_date: str | None = None


def _detect_year(text: str) -> int | None:
    m = re.search(r"\b(20\d{2})\b", text)
    return int(m.group(1)) if m else None


def extract_candidates(html: str, base_url: str) -> list[Candidate]:
    soup = BeautifulSoup(html, "html.parser")
    candidates = []
    for a in soup.find_all("a", href=True):
        href = a.get("href", "").strip()
        text = " ".join(a.get_text(" ", strip=True).split())
        full_url = urljoin(base_url, href)
        combined = f"{text} {full_url}"
        year = _detect_year(combined)
        ext = full_url.split("?")[0].split(".")[-1].lower() if "." in full_url else ""
        candidates.append(Candidate(full_url, text, ext, year))
    return candidates


MONTH_TO_NUMBER = {
    "january": 1,
    "february": 2,
    "march": 3,
    "april": 4,
    "may": 5,
    "june": 6,
    "july": 7,
    "august": 8,
    "september": 9,
    "october": 10,
    "november": 11,
    "december": 12,
}

CMS_PCS_DATED_UPDATE_RE = re.compile(
    r"/files/document/(?P<month>january|february|march|april|may|june|july|august|september|october|november|december)-(?P<day>[1-9]|[12][0-9]|3[01])-(?P<year>20\d{2})-official-icd-10-pcs-coding-guidelines\.pdf$",
    re.IGNORECASE,
)


def annotate_cms_pcs_candidate(cand: Candidate) -> Candidate | None:
    url = cand.url.split("?")[0]
    m_dated = CMS_PCS_DATED_UPDATE_RE.search(url)
    if m_dated:
        month = m_dated.group("month").lower()
        day = int(m_dated.group("day"))
        year = int(m_dated.group("year"))
        cand.year = year
        cand.document_kind = "dated_update"
        cand.effective_month = month
        cand.effective_day = day
        cand.effective_date = f"{year:04d}-{MONTH_TO_NUMBER[month]:02d}-{day:02d}"
        return cand
    return None
