"""Index construction.  [PHASE 2 — Week 4]

Builds the two search indexes over the document chunks:
a BM25 keyword index and a dense vector index (ChromaDB).
Not yet implemented — see ROADMAP.md, Week 4.
"""

from __future__ import annotations


def build_bm25_index(chunks: list) -> object:
    """Build a BM25 keyword index over the chunks.

    TODO (Week 4):
      - Use the ``rank-bm25`` package.
      - Tokenise each chunk's text; keep a parallel list of chunk metadata.
      - Return an object that can score a query against all chunks.
    """
    raise NotImplementedError("Phase 2, Week 4 — implement BM25 index. See ROADMAP.md")


def build_vector_index(chunks: list) -> object:
    """Build a dense vector index over the chunks.

    TODO (Week 4):
      - Embed each chunk with the sentence-transformer named in
        config/settings.yaml (retrieval.dense_model).
      - Store vectors + metadata in a ChromaDB collection.
      - Return the collection handle.
    """
    raise NotImplementedError("Phase 2, Week 4 — implement vector index. See ROADMAP.md")
