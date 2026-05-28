"""Evaluation and benchmarking.  [PHASE 3 — Weeks 7-8]

Scores both retrieval quality and answer quality against FinanceBench, and
produces the ablation table reported in the README.
Not yet implemented — see ROADMAP.md, Week 7.
"""

from __future__ import annotations


def evaluate_retrieval(predictions: list, gold: list) -> dict:
    """Compute retrieval metrics.

    TODO (Week 7):
      - Compute Recall@k, MRR, and nDCG@10.
      - "Gold" is the FinanceBench evidence passage for each question.
    """
    raise NotImplementedError("Phase 3, Week 7 — implement retrieval metrics. See ROADMAP.md")


def evaluate_answers(predictions: list, gold: list) -> dict:
    """Compute answer-quality metrics.

    TODO (Week 7):
      - Use RAGAS / DeepEval for faithfulness, answer relevancy, correctness.
      - Compare predictions against FinanceBench gold answers.
    """
    raise NotImplementedError("Phase 3, Week 7 — implement answer metrics. See ROADMAP.md")
