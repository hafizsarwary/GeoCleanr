"""Top-level package for GeoCleanr."""

from .validator import GeometryValidator, ValidationIssue
from .fixer import CoordinateFixer
from .reporter import ReportBuilder
from .visualizer import AsciiHeatmap

__all__ = [
    "GeometryValidator",
    "ValidationIssue",
    "CoordinateFixer",
    "ReportBuilder",
    "AsciiHeatmap",
]
