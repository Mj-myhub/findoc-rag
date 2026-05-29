"""Evaluation: retrieval recall against FinanceBench gold evidence.  [PHASE 3]"""

from __future__ import annotations

import re


def _norm_tokens(text: str) -> set:
    """Lowercase, drop commas (so 1,577 == 1577), split into word/number tokens."""
    text = text.replace(",", "").lower()
    return set(re.findall(r"[a-z0-9]+", text))


def gold_evidence_text(evidence) -> str:
    """Concatenate the gold evidence_text snippets for one question."""
    if evidence is None:
        return ""
    parts = []
    for e in evidence:
        try:
            t = e["evidence_text"]
        except (KeyError, TypeError, IndexError):
            t = None
        if t:
            parts.append(str(t))
    return " ".join(parts)


def best_overlap(gold_text: str, chunks: list) -> float:
    """Highest fraction of gold tokens found in any single retrieved chunk."""
    gold = _norm_tokens(gold_text)
    if not gold:
        return 0.0
    best = 0.0
    for c in chunks:
        ct = _norm_tokens(c["text"])
        best = max(best, len(gold & ct) / len(gold))
    return best
