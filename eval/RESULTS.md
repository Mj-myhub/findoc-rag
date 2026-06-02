# Evaluation Results

## Setup
- **Slice:** 15 SEC 10-K filings, 57 FinanceBench questions (see `data/DATA_CARD.md`).
- **Metric:** retrieval recall. For each question we retrieve the top-10 chunks and
  measure the largest fraction of gold-evidence tokens found in any single chunk
  (commas removed so "1,577" == "1577"); a hit means that overlap is >= 0.50.
  This is a heuristic proxy, so treat absolute values as directional.

## Baseline ablation (chunk_size = 800, overlap = 100)

| Configuration     | Recall@10 | Avg. overlap |
|-------------------|-----------|--------------|
| BM25 (keyword)    | 10.5%     | 0.26         |
| Dense (meaning)   | 21.1%     | 0.35         |
| Hybrid (RRF)      | 22.8%     | 0.35         |
| Hybrid + reranker | 24.6%     | 0.35         |

Dense beats keyword (questions rarely match the filing's wording); hybrid beats
either alone; reranking adds a final lift. Each component earns its place — but
absolute recall is low, especially on numerical / financial-statement questions.

## Tuning experiments

### Larger candidate pool (no lift)
Tested hybrid + rerank with candidate pool sizes 10, 30, 50.

| Pool size | Recall@10 |
|-----------|-----------|
| 10        | 24.6%     |
| 30        | 24.6%     |
| 50        | 21.1%     |

Recall did not improve, and pool=50 dropped — flooding the reranker with look-alikes
pushes the right chunk out. Conclusion: the right chunks are *not* reachable by
simply casting a wider net. The bottleneck is structural.

### Larger chunks (chunk_size = 1500, overlap = 300)

| Configuration     | Before (800) | After (1500) | Δ          |
|-------------------|--------------|--------------|------------|
| BM25              | 10.5%        | 19.3%        | +8.8 pts   |
| Dense             | 21.1%        | 33.3%        | +12.2 pts  |
| Hybrid            | 22.8%        | 29.8%        | +7.0 pts   |
| Hybrid + reranker | **24.6%**    | **33.3%**    | **+8.7 pts** |

Average best-overlap moved from 0.35 to 0.46.

## Honest interpretation
The chunk-size lift is real but partly mechanical: larger chunks contain more text,
so by chance they include more gold tokens, which boosts an overlap-based metric.

The metric-independent test: the 3M FY2018 capital-expenditure question (gold
answer $1,577M) **still abstains** under the larger chunks. Retrieval does not
surface the cash-flow chunk containing the figure. So while the metric improved
broadly, the core problem for numerical / table questions persists: the matching
signal between "capital expenditure" (the question) and "Purchases of property,
plant and equipment" (the line item) is weak in both keyword and embedding space.

## Key finding
Retrieval is reliable on **descriptive** questions and unreliable on **numerical /
financial-statement** questions. Larger chunks help on the margin but do not fix
the core failure mode, which is rooted in PDF table extraction scattering row
labels away from their values.

## Next steps
- Table-aware extraction so financial-statement rows stay intact (pdfplumber, unstructured).
- Query rewriting / vocabulary expansion ("capital expenditure" => "Purchases of property, plant and equipment").
- Split recall by question type (descriptive vs numerical) for a precise breakdown.
- Add answer-quality metrics (faithfulness, correctness) layered on top of retrieval recall.

## v0.5.0 — Cracking the numerical-question failure (three-layer investigation)

One question failed across *every* earlier experiment: the FY2018 capital
expenditure for 3M (gold answer: $1,577M). Tracing it revealed three stacked
root causes, each hiding the next.

**Layer 1 - Ranking?** Growing the candidate pool (10 -> 30 -> 50) gave no lift
(24.6% -> 24.6% -> 21.1%). Not a ranking-depth problem.

**Layer 2 - Extraction.** grep showed pypdf scattered the row label
("Purchases of property, plant and equipment") ~3 lines from its value
"(1,577)". Table-aware extraction (pdfplumber) put them back on one line.
Necessary, but on its own it did not fix the question, and table-row noise
slightly lowered the keyword/hybrid scores:

| Config | pypdf @1500 | pdfplumber @1500 |
|---|---|---|
| dense | 33.3% | 35.1% |
| bm25 | 19.3% | 17.5% |
| hybrid | 29.8% | 26.3% |
| hybrid+rerank | 33.3% | 31.6% |

**Layer 3 - Vocabulary (root cause).** Re-asking with the filing's own words
("purchases of property, plant and equipment") returned $1,577 instantly. The
question said "capital expenditure"; the filing never does. BM25 cannot match
the synonyms and the embedder does not bridge them well enough to rank the row
in the top 10.

**Fix: LLM query expansion.** Before retrieval, the question is rewritten into
likely 10-K line-item terminology, then searched with both. The original
"capital expenditure" question now answers correctly (citing the pdfplumber
table row), and Recall@10 improves across all 57 questions:

| query expansion | Recall@10 | avg overlap |
|---|---|---|
| OFF | 31.6% | 0.44 |
| ON  | 38.6% | 0.49 |

**Takeaway.** The two fixes compound: table-aware extraction makes the value
retrievable; query expansion makes it findable. End to end, hybrid+rerank
Recall@10 rose from 24.6% (initial baseline) to 38.6%, and numerical/line-item
questions that always abstained now answer with citations.
