---
title: FinDocRAG
colorFrom: blue
colorTo: indigo
sdk: gradio
sdk_version: 6.15.2
app_file: app.py
python_version: "3.12"
pinned: false
short_description: Q and A over SEC 10-K filings with citations and abstention
---

# FinDocRAG - Financial Document Q&A

Ask plain-English questions about 15 real SEC 10-K filings. Answers are grounded in the filings, cite their exact source passages, and abstain ("I cannot find this in the filings") rather than guessing.

Built with hybrid retrieval (BM25 + dense embeddings + reciprocal rank fusion), cross-encoder reranking, LLM query expansion, and a strict cite-or-abstain prompt.

Code and write-up: https://github.com/Mj-myhub/findoc-rag
