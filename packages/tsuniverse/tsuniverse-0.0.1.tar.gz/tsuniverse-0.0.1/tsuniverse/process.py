"""The main process function."""

from multiprocessing import Pool
from typing import Iterator

import pandas as pd

from .feature import Feature
from .pearson_process import pearson_process


def process(
    df: pd.DataFrame,
    predictands: list[str],
    max_window: int,
    max_process_features: int = 10,
) -> Iterator[list[Feature]]:
    """Process the dataframe for tsuniverse features."""
    with Pool() as p:
        for predictand in predictands:
            features = sorted(
                list(pearson_process(df, predictand, max_window, p)),
                key=lambda x: abs(x["correlation"] if "correlation" in x else 0.0),
                reverse=True,
            )[:max_process_features]
            yield features
