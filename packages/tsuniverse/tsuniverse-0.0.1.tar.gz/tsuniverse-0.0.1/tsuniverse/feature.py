"""The base class for a feature."""

from typing import NotRequired, TypedDict


class Feature(TypedDict):
    """A description of a feature to use."""

    predictor: str
    predictand: str
    lag: NotRequired[int]
    correlation: NotRequired[float]
