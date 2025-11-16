"""Process GPU data for analysis and visualization."""

from typing import Any

import pandas as pd

from .filters import categorize_gpu, is_ml_relevant


def filter_ml_gpus(dataset: pd.DataFrame) -> pd.DataFrame:
    """Filter dataset to ML-relevant GPUs.

    Args:
        dataset: Raw GPU dataset

    Returns:
        Filtered DataFrame with only ML-relevant GPUs
    """
    # Apply ML relevance filter
    mask = dataset.apply(is_ml_relevant, axis=1)
    filtered = dataset[mask].copy()

    # Add category column
    filtered["category"] = filtered.apply(categorize_gpu, axis=1)

    # Filter out "other" category
    filtered = filtered[filtered["category"].isin(["professional", "consumer"])]

    return filtered


def calculate_statistics(dataset: pd.DataFrame) -> dict[str, Any]:
    """Calculate summary statistics for GPU dataset.

    Args:
        dataset: Filtered GPU dataset with category column

    Returns:
        Dictionary with statistics
    """
    stats: dict[str, Any] = {}

    # Overall statistics
    stats["total_gpus"] = len(dataset)
    stats["date_range"] = {
        "min": dataset["release_date"].min(),
        "max": dataset["release_date"].max(),
    }

    # Price statistics (filter out missing prices)
    priced = dataset[dataset["price"].notna() & (dataset["price"] > 0)]
    stats["price_completeness"] = len(priced) / len(dataset) if len(dataset) > 0 else 0

    if len(priced) > 0:
        stats["price_overall"] = {
            "min": priced["price"].min(),
            "max": priced["price"].max(),
            "median": priced["price"].median(),
        }

        # Per-category statistics
        for category in ["professional", "consumer"]:
            cat_data = priced[priced["category"] == category]
            if len(cat_data) > 0:
                stats[f"price_{category}"] = {
                    "count": len(cat_data),
                    "min": cat_data["price"].min(),
                    "max": cat_data["price"].max(),
                    "median": cat_data["price"].median(),
                }
            else:
                stats[f"price_{category}"] = {
                    "count": 0,
                    "min": None,
                    "max": None,
                    "median": None,
                }

    # Performance statistics
    perf = dataset[dataset["fp32_tflops"].notna()]
    stats["performance_completeness"] = (
        len(perf) / len(dataset) if len(dataset) > 0 else 0
    )

    return stats


def prepare_time_series(
    dataset: pd.DataFrame, category: str | None = None
) -> pd.DataFrame:
    """Prepare data for time series plotting.

    Args:
        dataset: Filtered GPU dataset
        category: Optional category filter ("professional" or "consumer")

    Returns:
        DataFrame sorted by date, optionally filtered by category
    """
    df = dataset.copy()

    # Filter by category if specified
    if category is not None:
        df = df[df["category"] == category]

    # Filter to rows with valid price and date
    df = df[df["price"].notna() & (df["price"] > 0)]
    df = df[df["release_date"].notna()]

    # Sort by date
    df = df.sort_values("release_date")

    # Add year column for easier plotting
    df["year"] = df["release_date"].dt.year

    return df