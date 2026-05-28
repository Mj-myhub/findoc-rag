"""Compute statistics for the Week 2 slice (the 15 chosen filings)."""
import pandas as pd

df = pd.read_parquet("data/raw/financebench.parquet")

FILINGS = [
    "AMD_2022_10K", "AMERICANEXPRESS_2022_10K", "BOEING_2022_10K",
    "PEPSICO_2022_10K", "AMCOR_2023_10K", "3M_2022_10K",
    "AES_2022_10K", "BESTBUY_2023_10K", "CVSHEALTH_2022_10K",
    "JOHNSON_JOHNSON_2022_10K", "PFIZER_2021_10K", "VERIZON_2022_10K",
    "3M_2018_10K", "ACTIVISIONBLIZZARD_2019_10K", "ADOBE_2022_10K",
]

slice_df = df[df["doc_name"].isin(FILINGS)]

print("Total questions in slice:", len(slice_df))
print("Unique companies:", slice_df["company"].nunique())
print("Unique filings:", slice_df["doc_name"].nunique())
print("\nBy question_type:")
print(slice_df["question_type"].value_counts())
print("\nBy GICS sector:")
print(slice_df["gics_sector"].value_counts())
print("\nBy document period (year):")
print(slice_df["doc_period"].value_counts().sort_index())
