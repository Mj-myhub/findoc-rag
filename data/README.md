# data/

This folder holds datasets and filings. **Its contents are git-ignored** — large data files
should not live in the repository.

- `raw/` — downloaded data as-is (FinanceBench parquet, source filing text).
- `processed/` — data produced by the pipeline (e.g. `chunks.parquet`).

To populate `raw/`, run:

```bash
make explore
```

In Week 2 you will also add a `DATA_CARD.md` here describing your chosen evaluation slice.
