"""Filter GPUs by relevance to machine learning and scientific computing."""

from typing import Literal

import pandas as pd


def is_ml_relevant(gpu_row: pd.Series) -> bool:
    """Check if GPU is relevant for ML/scientific computing workloads.

    Args:
        gpu_row: Single row from GPU dataset

    Returns:
        True if GPU should be included in analysis
    """
    name_lower = str(gpu_row.get("name", "")).lower()

    # Exclude mobile/embedded GPUs
    if any(x in name_lower for x in ["mobile", "laptop", "max-q", "maxq"]):
        return False

    # Include professional datacenter GPUs
    if any(
        x in name_lower
        for x in ["tesla", "a100", "h100", "v100", "p100", "a6000", "rtx 6000"]
    ):
        return True

    # Include consumer cards with sufficient performance (SLEAP-compatible)
    if "rtx" in name_lower or "gtx" in name_lower:
        # Check FP32 performance as proxy for ML capability
        fp32 = gpu_row.get("fp32_tflops", 0)
        if pd.notna(fp32) and fp32 >= 5.0:
            return True

    return False


def categorize_gpu(gpu_row: pd.Series) -> Literal["professional", "consumer", "other"]:
    """Categorize GPU into professional or consumer class.

    Args:
        gpu_row: Single row from GPU dataset

    Returns:
        Category: "professional", "consumer", or "other"
    """
    name_lower = str(gpu_row.get("name", "")).lower()

    # Professional datacenter GPUs
    if any(
        x in name_lower
        for x in [
            "tesla",
            "a100",
            "h100",
            "v100",
            "p100",
            "a6000",
            "a5000",
            "a4000",
            "rtx 6000",
            "rtx 5000",
            "rtx 4000",
        ]
    ):
        return "professional"

    # Consumer RTX/GTX series
    if any(x in name_lower for x in ["rtx", "gtx"]):
        # Exclude professional RTX (already handled above)
        if "6000" not in name_lower and "5000" not in name_lower:
            return "consumer"

    return "other"
