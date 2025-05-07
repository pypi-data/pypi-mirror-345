"""The pearson process function."""

from typing import Any, Iterator

import numpy as np
import pandas as pd

from .feature import Feature

_PEARSON_CACHE: dict[str, Feature] = {}


def pearson_correlation_positive_lags(
    x: pd.Series, y: pd.Series, max_window: int
) -> Feature:
    """Calculate the best pearson correlation for the 2 series within a lag window"""
    corrs = []
    lags = range(1, max_window + 1)

    for lag in lags:
        y_shifted = y.shift(lag)
        valid_idx = x.index.intersection(y_shifted.index)  # type: ignore
        corr = x.loc[valid_idx].corr(y_shifted.loc[valid_idx])
        corrs.append(corr)

    best_idx = np.argmax(np.abs(corrs))
    best_lag = lags[best_idx]
    best_corr = corrs[best_idx]
    if np.isnan(best_corr):
        best_corr = 0.0

    return {
        "predictor": str(y.name),
        "predictand": str(x.name),
        "lag": float(best_lag),
        "correlation": float(best_corr),
    }


def pearson_process(
    df: pd.DataFrame,
    predictand: str,
    max_window: int,
    pool: Any,
) -> Iterator[Feature]:
    """Process the dataframe for tsuniverse features."""
    predictors = df.columns.values.tolist()
    cached_predictors = []
    for predictor in predictors:
        key = "_".join(sorted([predictor, predictand]))
        feature = _PEARSON_CACHE.get(key)
        if feature is not None:
            yield feature
            cached_predictors.append(predictor)
    for feature in pool.starmap(
        pearson_correlation_positive_lags,
        [
            (df[x], df[predictand], max_window)
            for x in df.columns.values.tolist()
            if x != predictand and x not in cached_predictors
        ],
    ):
        if feature is None:
            continue
        key = "_".join(sorted([feature["predictor"], feature["predictand"]]))
        _PEARSON_CACHE[key] = feature
        yield feature
