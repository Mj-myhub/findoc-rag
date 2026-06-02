# FinDocRAG

Ask plain-English questions about SEC 10-K annual reports and get answers grounded in the filing text — with citations, or an honest "I cannot find this" when the answer isn't there.

A retrieval-augmented generation (RAG) system built from scratch over real financial filings, with a measured, honest evaluation.

## What it does

10-K filings run 100–200 pages of dense financial and legal text. FinDocRAG answers questions like *"What are AMD's main business risks?"* with a short response that cites the exact passages it used — and refuses to guess when the answer isn't in the filings.

> **Q:** What are the main business risks for AMD?
> **A:** Intel's dominance of the microprocessor market; global economic uncertainty; reliance on external financing. *[cites AMD_2022_10K::57, ::60, ::6]*

> **Q:** What is the capital of France?
> **A:** I cannot find this in the filings.

## How it works

```mermaid
flowchart LR
    Q[Question] --> B[BM25 keyword search]
    Q --> D[Dense vector search]
    B --> F[Reciprocal Rank Fusion]
    D --> F
    F --> R[Cross-encoder rerank]
    R --> L[LLM: grounded, cited answer or abstain]
```

- **Chunking:** filings split into 1,500-character overlapping passages
- **Keyword index:** BM25 (`rank-bm25`)
- **Vector index:** `BAAI/bge-small-en-v1.5` embeddings in ChromaDB
- **Fusion:** Reciprocal Rank Fusion merges both rankings
- **Reranking:** `BAAI/bge-reranker-base` cross-encoder re-scores candidates
- **Generation:** Groq `llama-3.1-8b-instant` with a strict cite-or-abstain prompt
- **Interfaces:** FastAPI endpoint (`POST /ask`) and a Gradio web demo

## Results

Evaluated on 57 expert-written questions from [FinanceBench](https://github.com/patronus-ai/financebench) across a 15-filing slice. Metric: retrieval Recall@10 by gold-evidence overlap. Full methodology in [eval/RESULTS.md](eval/RESULTS.md).

| Configuration     | Recall@10 |
|-------------------|-----------|
| BM25 (keyword)    | 19.3%     |
| Dense (meaning)   | 33.3%     |
| Hybrid (RRF)      | 29.8%     |
| Hybrid + reranker | **33.3%** |

Increasing chunk size from 800 to 1,500 characters lifted the best configuration from 24.6% to 33.3% (+8.7 points).

**Honest limitation:** retrieval is reliable on descriptive questions but weak on numerical questions that require reading financial-statement tables (e.g. capital expenditure), because PDF table extraction scatters row labels from their values. Documented, not hidden — see RESULTS.md.

## Quickstart

Requires Python 3.10+ and a free [Groq API key](https://console.groq.com).

```bash
# 1. Environment
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
pip install -e .

# 2. Add your Groq key
cp .env.example .env
# edit .env and set GROQ_API_KEY=gsk_...

# 3. Build data + indexes (downloads 15 filings; a few minutes)
python3 get_pdfs.py
python3 extract_text.py
python3 make_chunks.py
python3 build_vector_index.py
python3 build_bm25_index.py

# 4. Run the demo
python3 demo.py     # Gradio UI at http://127.0.0.1:7860
```

Or run the API:

```bash
uvicorn findoc_rag.api.app:app
# POST http://127.0.0.1:8000/ask  body: {"question": "..."}
```

## Tech stack

Python · sentence-transformers · ChromaDB · rank-bm25 · Groq · FastAPI · Gradio · pytest · ruff · GitHub Actions

## Status & future work

Complete through a working, evaluated, demoable system. Possible next steps: table-aware PDF extraction to fix numerical-question retrieval; answer-quality metrics (faithfulness, correctness); a permanently hosted demo.
