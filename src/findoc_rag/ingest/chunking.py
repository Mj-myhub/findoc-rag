"""Document chunking.  [PHASE 2 - Week 3]

Splits long filings into smaller, overlapping passages ("chunks") that can be
indexed and retrieved.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class Chunk:
    """A single passage from a filing, with metadata for citation."""

    text: str
    company: str
    doc_name: str
    chunk_id: str
    start_char: int
    end_char: int


def chunk_text(
    text: str,
    company: str,
    doc_name: str,
    chunk_size: int = 800,
    overlap: int = 100,
) -> list[Chunk]:
    """Split one filing into overlapping fixed-size chunks.

    Uses a sliding window: take chunk_size characters, then slide forward by
    (chunk_size - overlap) so neighbouring chunks share `overlap` characters.
    """
    chunks: list[Chunk] = []
    if not text:
        return chunks

    step = chunk_size - overlap          # how far the window moves each time
    index = 0                            # counts the chunks, for unique ids
    start = 0

    while start < len(text):
        end = min(start + chunk_size, len(text))
        chunks.append(
            Chunk(
                text=text[start:end],
                company=company,
                doc_name=doc_name,
                chunk_id=f"{doc_name}::{index}",
                start_char=start,
                end_char=end,
            )
        )
        index += 1
        if end == len(text):             # reached the end; stop
            break
        start += step                    # slide the window forward

    return chunks
