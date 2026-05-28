# FinDocRAG

**A Retrieval-Augmented Generation system for question answering over SEC 10-K filings.**

> Status: 🟡 In development — Phase 1 (Foundation). See [ROADMAP.md](ROADMAP.md) for the full build plan.

---

## The problem

Company annual reports (SEC 10-K filings) routinely run 100–200+ pages. An analyst who needs
one specific disclosure — a risk factor, a revenue figure, a segment note — has to read or
keyword-hunt through the whole document. FinDocRAG lets a user **ask a question in plain English
and get a grounded answer with a citation back to the exact passage** in the filing.

This is a recognised, high-value industrial use case: financial-document analysis is one of the
most common enterprise applications of RAG, and dedicated commercial products exist for it.

## What it does (target system)

```
        Question: "What are Apple's main supply-chain risks?"
                              │
                              ▼
   ┌──────────────────────────────────────────────────────┐
   │  1. Retrieve  →  BM25 + dense embeddings (hybrid)      │
   │  2. Rerank    →  cross-encoder reranker                │
   │  3. Generate  →  LLM answers ONLY from retrieved text  │
   │  4. Cite      →  answer + source passage references    │
   │  5. Abstain   →  says "not found" instead of guessing  │
   └──────────────────────────────────────────────────────┘
                              │
                              ▼
     Answer + citations  +  full request trace (Langfuse)
```

Every component is **measured**: the system is evaluated against
[FinanceBench](https://github.com/patronus-ai/financebench), an external benchmark of expert-written
questions over real filings.

## Tech stack

| Layer          | Tools |
|----------------|-------|
| Language       | Python 3.10+ |
| Retrieval      | `rank-bm25`, `sentence-transformers`, ChromaDB |
| Reranking      | `BAAI/bge-reranker` cross-encoder |
| Generation     | Groq API (free tier) — Llama 3.1 |
| Evaluation     | RAGAS, DeepEval, FinanceBench |
| Observability  | Langfuse |
| Serving        | FastAPI + Streamlit |
| Packaging      | Docker, GitHub Actions CI |

## Quickstart

```bash
# 1. Clone and enter the project
git clone https://github.com/Mj-myhub/findoc-rag.git
cd findoc-rag

# 2. (Recommended) create a virtual environment
python -m venv .venv && source .venv/bin/activate   # Windows: .venv\Scripts\activate

# 3. Install
make install            # or: pip install -r requirements.txt && pip install -e .

# 4. Download the evaluation dataset
make explore            # loads FinanceBench, saves a local copy, prints its structure

# 5. Run the tests
make test
```

## Day 1 checklist

- [ ] Read this README and [ROADMAP.md](ROADMAP.md) end to end.
- [ ] Create the GitHub repo `findoc-rag` and push this code to it.
- [ ] Run `make install` successfully.
- [ ] Run `make explore` — confirm `data/raw/financebench.parquet` is created.
- [ ] Open `notebooks/01_explore_financebench.ipynb` and read through the dataset.
- [ ] You should now be able to describe, in your own words, what FinanceBench contains.

## Results

_To be filled in during Phase 3. The headline deliverable is an ablation table showing how much
each component (hybrid retrieval, reranking) improves answer quality._

| Configuration            | Recall@10 | nDCG@10 | Faithfulness | Answer correctness |
|--------------------------|-----------|---------|--------------|--------------------|
| Dense retrieval only     | _TBD_     | _TBD_   | _TBD_        | _TBD_              |
| BM25 only                | _TBD_     | _TBD_   | _TBD_        | _TBD_              |
| Hybrid (BM25 + dense)    | _TBD_     | _TBD_   | _TBD_        | _TBD_              |
| Hybrid + reranker        | _TBD_     | _TBD_   | _TBD_        | _TBD_              |

## Repository layout

```
findoc-rag/
├── README.md              ← you are here
├── ROADMAP.md             ← the week-by-week build plan
├── ARCHITECTURE.md        ← system design and rationale
├── config/settings.yaml   ← all tunable settings
├── src/findoc_rag/        ← the Python package
│   ├── data/              ← dataset loading (Phase 1 — done)
│   ├── ingest/            ← chunking (Phase 2)
│   ├── index/             ← BM25 + vector index (Phase 2)
│   ├── retrieval/         ← hybrid retrieval + reranking (Phase 2)
│   ├── generate/          ← LLM answer generation (Phase 2)
│   ├── evaluation/        ← metrics and benchmarking (Phase 3)
│   └── api/               ← FastAPI service (Phase 4)
├── notebooks/             ← exploration notebooks
├── eval/                  ← evaluation results
└── tests/                 ← automated tests
```

## License

MIT — see [LICENSE](LICENSE).

_FinanceBench is released by Patronus AI under its own license; review it before redistributing
any derived data._

## Disclaimer

FinDocRAG is a portfolio and research project. It does **not** provide financial advice and
should not be used for investment decisions.
