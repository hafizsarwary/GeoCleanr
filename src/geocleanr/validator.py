from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, Any, List


@dataclass(frozen=True)
class ValidationIssue:
    """Small container describing what failed and where."""

    index: int
    field: str
    message: str


class GeometryValidator:
    """Validate latitude/longitude pairs stored in mapping-like rows."""

    def __init__(
        self,
        lat_field: str = "lat",
        lon_field: str = "lon",
        precision: int | None = None,
    ) -> None:
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.precision = precision

    def validate(self, rows: Iterable[Mapping[str, Any]]) -> List[ValidationIssue]:
        issues: List[ValidationIssue] = []
        for idx, row in enumerate(rows):
            lat = row.get(self.lat_field)
            lon = row.get(self.lon_field)
            if lat is None or lon is None:
                issues.append(
                    ValidationIssue(idx, "coordinates", "Missing latitude or longitude")
                )
                continue

            if not self._within_range(lat, -90, 90):
                issues.append(ValidationIssue(idx, self.lat_field, "Latitude outside bounds"))
            if not self._within_range(lon, -180, 180):
                issues.append(
                    ValidationIssue(idx, self.lon_field, "Longitude outside bounds")
                )

            if self.precision is not None and not self._has_precision(lat, lon):
                issues.append(
                    ValidationIssue(
                        idx,
                        "precision",
                        f"Expected {self.precision} decimal places",
                    )
                )
        return issues

    def is_valid(self, rows: Iterable[Mapping[str, Any]]) -> bool:
        return not self.validate(rows)

    def _within_range(self, value: Any, lower: float, upper: float) -> bool:
        try:
            return lower <= float(value) <= upper
        except (TypeError, ValueError):
            return False

    def _has_precision(self, lat: Any, lon: Any) -> bool:
        return all(self._count_decimals(value) >= self.precision for value in (lat, lon))

    def _count_decimals(self, value: Any) -> int:
        text = f"{value}"
        if "." not in text:
            return 0
        return len(text.split(".")[-1].rstrip("0"))
