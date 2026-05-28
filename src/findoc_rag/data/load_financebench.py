"""Load the FinanceBench evaluation dataset.

FinanceBench is a benchmark of expert-written questions and answers over real SEC
filings. FinDocRAG uses it as the gold standard for evaluation.

Run from the project root with:

    python -m findoc_rag.data.load_financebench

This downloads the dataset, prints its structure, and saves a local copy to
``data/raw/financebench.parquet``.
"""

from __future__ import annotations

import pandas as pd

from findoc_rag.config import RAW_DATA_DIR, SETTINGS


def load_financebench() -> pd.DataFrame:
    """Load FinanceBench from the Hugging Face Hub as a pandas DataFrame.

    Returns:
        The dataset as a DataFrame.

    Raises:
        ImportError: if the ``datasets`` package is not installed.
        RuntimeError: if the dataset id cannot be resolved on the Hub. The error
            message explains how to correct it.
    """
    try:
        from datasets import load_dataset
    except ImportError as exc:  # pragma: no cover - environment-dependent
        raise ImportError(
            "The 'datasets' package is required. Install it with:\n"
            "    pip install -r requirements.txt"
        ) from exc

    dataset_id = SETTINGS["data"]["financebench_dataset_id"]
    split = SETTINGS["data"]["financebench_split"]
    print(f"Loading FinanceBench  (dataset='{dataset_id}', split='{split}') ...")

    try:
        dataset = load_dataset(dataset_id, split=split)
    except Exception as exc:  # noqa: BLE001 - we re-raise with guidance
        raise RuntimeError(
            f"Could not load the dataset '{dataset_id}'.\n\n"
            "How to fix this:\n"
            "  1. Open https://huggingface.co/datasets and search for 'financebench'.\n"
            "  2. Copy the exact dataset id shown on the dataset page.\n"
            "  3. Open config/settings.yaml and set:\n"
            "         data.financebench_dataset_id: \"<the correct id>\"\n"
            "  4. Run this command again.\n\n"
            f"Underlying error: {exc}"
        ) from exc

    return dataset.to_pandas()


def main() -> None:
    """Download FinanceBench, summarise it, and save a local copy."""
    df = load_financebench()

    print(f"\nLoaded {len(df)} rows.")
    print(f"Columns ({len(df.columns)}): {list(df.columns)}\n")
    print("First row preview:")
    print("-" * 60)
    for column in df.columns:
        value = str(df.iloc[0][column])
        preview = value if len(value) <= 200 else value[:200] + " ..."
        print(f"{column}: {preview}")
    print("-" * 60)

    RAW_DATA_DIR.mkdir(parents=True, exist_ok=True)
    output_path = RAW_DATA_DIR / "financebench.parquet"
    df.to_parquet(output_path)
    print(f"\nSaved a local copy to: {output_path}")
    print("Next: open notebooks/01_explore_financebench.ipynb (see ROADMAP.md, Week 1).")


if __name__ == "__main__":
    main()
