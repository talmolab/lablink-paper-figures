"""Load and validate GPU pricing data from Epoch AI dataset."""

from pathlib import Path

import pandas as pd


def load_gpu_dataset(path: str | Path) -> pd.DataFrame:
    """Load GPU dataset from Epoch AI ML Hardware CSV.

    Args:
        path: Path to ml_hardware.csv file

    Returns:
        DataFrame with GPU pricing and performance data

    Raises:
        FileNotFoundError: If dataset file doesn't exist
        ValueError: If required columns are missing or data is malformed
    """
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(
            f"GPU dataset not found at {path}\n\n"
            "Please download the Epoch AI Machine Learning Hardware Database:\n"
            "1. Visit: https://epoch.ai/data/machine-learning-hardware\n"
            "2. Click 'Download Data' to get the CSV file\n"
            "3. Extract the ZIP and place ml_hardware.csv in data/raw/gpu_prices/\n\n"
            "See data/raw/gpu_prices/README.md for detailed instructions."
        )

    try:
        df = pd.read_csv(path)
    except Exception as e:
        raise ValueError(f"Failed to parse CSV file: {e}")

    # Map Epoch AI column names to our expected names
    column_mapping = {
        "Hardware name": "name",
        "Release date": "release_date",
        "Release price (USD)": "price",
        "FP32 (single precision) performance (FLOP/s)": "fp32_flops",
    }

    # Rename columns
    df = df.rename(columns=column_mapping)

    # Validate required columns exist after mapping
    required_columns = ["name", "release_date", "price", "fp32_flops"]
    missing_columns = [col for col in required_columns if col not in df.columns]

    if missing_columns:
        raise ValueError(
            f"Dataset is missing required columns: {missing_columns}\n"
            f"Found columns: {list(df.columns)}\n"
            "Please ensure you're using the correct Epoch AI dataset."
        )

    # Convert FP32 FLOP/s to TFLOP/s
    df["fp32_tflops"] = df["fp32_flops"] / 1e12

    # Parse dates to datetime
    try:
        df["release_date"] = pd.to_datetime(df["release_date"])
    except Exception as e:
        raise ValueError(f"Failed to parse release_date column: {e}")

    # Validate date range (rough check for data quality)
    min_year = df["release_date"].dt.year.min()
    max_year = df["release_date"].dt.year.max()

    if min_year > 2015 or max_year < 2020:
        raise ValueError(
            f"Unexpected date range in dataset: {min_year}-{max_year}\n"
            "Expected data from ~2006-2025. Please verify dataset integrity."
        )

    return df
