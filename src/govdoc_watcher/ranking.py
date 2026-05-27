from govdoc_watcher.config import SourceConfig
from govdoc_watcher.discovery import Candidate, annotate_cms_pcs_candidate


def _is_cms_pcs_source(src: SourceConfig) -> bool:
    return src.id == "cms-icd10-pcs-guidelines"


def _matches_required(src: SourceConfig, cand: Candidate) -> bool:
    hay = f"{cand.link_text} {cand.url}".lower()
    return all(p.lower() in hay for p in src.required_text_patterns)


def _is_excluded(src: SourceConfig, cand: Candidate) -> bool:
    hay = f"{cand.link_text} {cand.url}".lower()
    return any(p.lower() in hay for p in src.exclude_text_patterns)


def score_candidate(src: SourceConfig, cand: Candidate) -> tuple[int, str]:
    if _is_excluded(src, cand):
        return (-9999, "excluded")
    if not _matches_required(src, cand):
        return (-5000, "missing required patterns")
    score = 100
    reasons = ["required patterns matched"]
    if cand.extension in [e.lower() for e in src.allowed_extensions]:
        score += 100
        reasons.append("allowed extension")
    if src.prefer_newest_year and cand.year:
        score += cand.year
        reasons.append(f"year={cand.year}")
    if src.prefer_april_update and cand.is_april_1:
        score += 50
        reasons.append("april-1 bonus")
    return score, ", ".join(reasons)


def pick_best(src: SourceConfig, candidates: list[Candidate]) -> tuple[Candidate | None, int, str]:
    if _is_cms_pcs_source(src):
        return pick_best_cms_pcs(src, candidates)
    ranked = sorted(((score_candidate(src, c), c) for c in candidates), key=lambda x: x[0][0], reverse=True)
    if not ranked or ranked[0][0][0] < 0:
        return None, -1, "no valid candidates"
    (score, reason), cand = ranked[0]
    return cand, score, reason


def pick_best_cms_pcs(src: SourceConfig, candidates: list[Candidate]) -> tuple[Candidate | None, int, str]:
    valid = []
    for cand in candidates:
        if cand.extension.lower() != "pdf":
            continue
        if _is_excluded(src, cand):
            continue
        matched = annotate_cms_pcs_candidate(cand)
        if not matched:
            continue
        valid.append(matched)
    if not valid:
        return None, -1, "no valid CMS PCS candidates"
    valid.sort(key=lambda c: (c.year or 0, 1 if (src.prefer_april_update and c.document_kind == "april_1") else 0), reverse=True)
    best = valid[0]
    return best, 1000 + (best.year or 0), f"cms-url-pattern kind={best.document_kind} year={best.year}"
