"""
MongoDB Aggregation Pipeline Builder
"""

__version__ = "0.1.0"

from .core import AggBuilder
from .exceptions import AggBuilderError, InvalidLookupError, PipelineSerializationError, InvalidStageError

__all__ = [
    "AggBuilder",
    "AggBuilderError",
    "InvalidLookupError",
    "PipelineSerializationError",
    "InvalidStageError"
]