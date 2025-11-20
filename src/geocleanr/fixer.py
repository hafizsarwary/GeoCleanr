from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, Tuple, Any, List

from .validator import GeometryValidator, ValidationIssue


@dataclass
class FixResult:
    record: dict
    fixes: list[str]


class CoordinateFixer:
    """Apply simple heuristics to repair broken coordinate pairs."""

    def __init__(
        self,
        lat_field: str = "lat",
        lon_field: str = "lon",
        fallback: Tuple[float, float] = (0.0, 0.0),
        clip: bool = True,
    ) -> None:
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.fallback = fallback
        self.clip = clip
        self.validator = GeometryValidator(lat_field=lat_field, lon_field=lon_field)

    def fix_record(self, record: Mapping[str, Any]) -> FixResult:
        mutable: MutableMapping[str, Any] = dict(record)
        fixes: list[str] = []

        lat = mutable.get(self.lat_field)
        lon = mutable.get(self.lon_field)

        if lat is None or lon is None:
            mutable[self.lat_field], mutable[self.lon_field] = self.fallback
            fixes.append("filled_missing")
            return FixResult(dict(mutable), fixes)

        lat, lon = self._ensure_float(lat, lon)
        swapped = lat is not None and lon is not None and self._looks_swapped(lat, lon)
        if swapped:
            lat, lon = lon, lat
            fixes.append("swapped_axes")

        if lat is None or lon is None:
            mutable[self.lat_field], mutable[self.lon_field] = self.fallback
            fixes.append("fallback_applied")
            return FixResult(dict(mutable), fixes)

        if self.clip:
            clipped_lat = self._clip(lat, -90, 90)
            clipped_lon = self._clip(lon, -180, 180)
            if clipped_lat != lat:
                fixes.append("lat_clipped")
            if clipped_lon != lon:
                fixes.append("lon_clipped")
            lat, lon = clipped_lat, clipped_lon

        mutable[self.lat_field] = lat
        mutable[self.lon_field] = lon
        return FixResult(dict(mutable), fixes)

    def fix_all(self, rows: Iterable[Mapping[str, Any]]) -> List[FixResult]:
        return [self.fix_record(row) for row in rows]

    def validate_after_fix(self, rows: Iterable[Mapping[str, Any]]) -> List[ValidationIssue]:
        fixed = (result.record for result in self.fix_all(rows))
        return self.validator.validate(fixed)

    def _ensure_float(self, lat: Any, lon: Any) -> Tuple[float | None, float | None]:
        try:
            lat_f = float(lat)
        except (TypeError, ValueError):
            lat_f = None
        try:
            lon_f = float(lon)
        except (TypeError, ValueError):
            lon_f = None
        return lat_f, lon_f

    def _looks_swapped(self, lat: float, lon: float) -> bool:
        return abs(lat) > 90 and abs(lon) <= 90

    def _clip(self, value: float, lower: float, upper: float) -> float:
        return min(max(value, lower), upper)
