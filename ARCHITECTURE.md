# FinDocRAG — Architecture

This document explains *how* the system is built and *why* each choice was made. It is written
to be read by a recruiter or engineer reviewing the project, so keep it updated as you build.

## 1. The pipeline

```
   ┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐
   │  10-K        │   │  Chunking    │   │  Indexing     │   │  Retrieval   │
   │  filings     │──▶│  (ingest/)   │──▶│  (index/)     │──▶│  (retrieval/)│
   │  (raw text)  │   │  passages +  │   │  BM25 +       │   │  hybrid RRF  │
   │              │   │  metadata    │   │  vector DB    │   │  + reranker  │
   └─────────────┘   └──────────────┘   └───────────────┘   └──────┬───────┘
                                                                    │
                                                                    ▼
   ┌─────────────┐   ┌──────────────┐   ┌───────────────┐   ┌──────────────┐
   │  User        │   │  FastAPI /   │   │  Generation   │   │  Retrieved   │
   │  question    │──▶│  Streamlit   │──▶│  (generate/)  │◀──│  passages    │
   │              │   │  (api/)      │   │  LLM + prompt │   │              │
   └─────────────┘   └──────────────┘   └───────┬───────┘   └──────────────┘
                                                │
                                                ▼
                              Answer + citations + abstention
                                                │
                                                ▼
                              Langfuse trace (every call logged)
```

## 2. Components and responsibilities

| Module        | Responsibility |
|---------------|----------------|
| `data/`       | Load FinanceBench (gold questions/answers); save local copies. |
| `ingest/`     | Split filings into overlapping, metadata-tagged chunks. |
| `index/`      | Build a BM25 keyword index and a dense vector index over the chunks. |
| `retrieval/`  | For a query: query both indexes, fuse with RRF, rerank with a cross-encoder. |
| `generate/`   | Build the prompt, call the LLM, enforce citation + abstention behaviour. |
| `evaluation/` | Score retrieval and answers against FinanceBench; produce the ablation table. |
| `api/`        | Expose the system as a FastAPI endpoint and a Streamlit demo. |

## 3. Key design decisions

**Why hybrid retrieval (BM25 + dense)?**
Dense embeddings capture meaning but miss exact identifiers — ticker symbols, line-item names,
specific figures — which matter a lot in financial text. BM25 (keyword search) catches those.
Combining both with Reciprocal Rank Fusion is the production-standard baseline and reliably
beats either method alone on noisy document collections.

**Why a reranker?**
First-stage retrieval optimises for recall (get the right passage *somewhere* in the top 20).
A cross-encoder reranker then re-scores those candidates with a more accurate but slower model,
pushing the truly relevant passage to the top. Retrieval quality is the single biggest driver
of final RAG quality, so this stage earns its cost.

**Why abstention?**
A system that confidently invents an answer when the filing does not contain one is worse than
useless in finance. The generator is explicitly prompted to say "I cannot find this in the
filings" when the retrieved context is insufficient. Abstention rate on unanswerable questions
is a tracked metric.

**Why evaluate against FinanceBench instead of self-written questions?**
Self-written evaluation questions are easy to game and unconvincing to a reviewer. FinanceBench
is an external, expert-written benchmark — measuring against it makes the results credible.

**Why Groq for the LLM?**
The project must be free to run. Groq offers a free API tier with fast inference for open
models (Llama 3.1). Generation is the only component that calls an external service; everything
else runs locally or on free Colab.

## 4. Data flow at query time

1. User submits a question.
2. The question is embedded and also tokenised for BM25.
3. Both indexes return their top-k chunks; RRF merges them into one ranked list.
4. The cross-encoder reranker re-scores the merged list; the top-N chunks are kept.
5. Those chunks + the question go into the prompt.
6. The LLM produces an answer, with inline references to chunk IDs, or abstains.
7. The full trace (query, chunks, scores, prompt, output, latency) is logged to Langfuse.

## 5. What is intentionally simple

This is a portfolio project, not a production deployment. It deliberately does **not** include:
multi-tenant auth, autoscaling, a managed vector database, or streaming responses. The focus is
on demonstrating correct retrieval design, rigorous evaluation, and clean engineering — the
skills junior NLP/LLM roles actually screen for.
