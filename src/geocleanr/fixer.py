from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, Mapping, MutableMapping, Tuple, Any, List

from .validator import GeometryValidator, ValidationIssue


@dataclass
class FixResult:
    # Clean record plus a small audit trail.
    record: dict
    fixes: list[str]
    changes: dict[str, Tuple[Any, Any]]


class CoordinateFixer:
    """Apply simple heuristics to repair broken coordinate pairs."""

    def __init__(
        self,
        lat_field: str = "lat",
        lon_field: str = "lon",
        fallback: Tuple[float, float] = (0.0, 0.0),
        clip: bool = True,
        max_abs: float | None = None,
    ) -> None:
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.fallback = fallback
        self.clip = clip
        self.max_abs = max_abs
        self.validator = GeometryValidator(lat_field=lat_field, lon_field=lon_field)

    def fix_record(self, record: Mapping[str, Any]) -> FixResult:
        mutable: MutableMapping[str, Any] = dict(record)
        fixes: list[str] = []
        changes: dict[str, Tuple[Any, Any]] = {}

        # Pull raw values from the input record.
        lat = mutable.get(self.lat_field)
        lon = mutable.get(self.lon_field)

        # Try to turn both values into floats, note any coercions.
        lat, lat_note, lat_changed = self._coerce_value(lat)
        lon, lon_note, lon_changed = self._coerce_value(lon)
        fixes.extend(lat_note)
        fixes.extend(lon_note)
        if lat_changed:
            changes[self.lat_field] = (record.get(self.lat_field), lat)
        if lon_changed:
            changes[self.lon_field] = (record.get(self.lon_field), lon)

        # If both are missing or broken, drop in the fallback pair.
        if lat is None and lon is None:
            mutable[self.lat_field], mutable[self.lon_field] = self.fallback
            fixes.append("filled_missing")
            changes[self.lat_field] = (record.get(self.lat_field), self.fallback[0])
            changes[self.lon_field] = (record.get(self.lon_field), self.fallback[1])
            return FixResult(dict(mutable), fixes, changes)

        # Fill only the missing side so we do not lose a good value.
        if lat is None:
            lat = self.fallback[0]
            fixes.append("lat_filled")
            changes[self.lat_field] = (record.get(self.lat_field), lat)
        if lon is None:
            lon = self.fallback[1]
            fixes.append("lon_filled")
            changes[self.lon_field] = (record.get(self.lon_field), lon)

        # Swap if numbers look like they are in the wrong columns.
        swapped = self._looks_swapped(lat, lon)
        if swapped:
            lat, lon = lon, lat
            fixes.append("swapped_axes")
            changes[self.lat_field] = (record.get(self.lat_field), lat)
            changes[self.lon_field] = (record.get(self.lon_field), lon)

        # Normalize 0–360 longitudes to the usual -180–180 range.
        wrapped_lon, wrapped = self._wrap_longitude(lon)
        if wrapped:
            fixes.append("lon_wrapped")
            changes[self.lon_field] = (lon, wrapped_lon)
        lon = wrapped_lon

        # If max_abs is set, throw away extreme outliers.
        lat, lat_outlier = self._handle_outlier(lat, self.fallback[0])
        lon, lon_outlier = self._handle_outlier(lon, self.fallback[1])
        if lat_outlier:
            fixes.append("lat_outlier")
            changes[self.lat_field] = (record.get(self.lat_field), lat)
        if lon_outlier:
            fixes.append("lon_outlier")
            changes[self.lon_field] = (record.get(self.lon_field), lon)

        if self.clip:
            # Push values back into legal ranges if they are slightly off but not extreme.
            clipped_lat = self._clip(lat, -90, 90)
            clipped_lon = self._clip(lon, -180, 180)
            if clipped_lat != lat:
                fixes.append("lat_clipped")
                changes[self.lat_field] = (lat, clipped_lat)
            if clipped_lon != lon:
                fixes.append("lon_clipped")
                changes[self.lon_field] = (lon, clipped_lon)
            lat, lon = clipped_lat, clipped_lon

        mutable[self.lat_field] = lat
        mutable[self.lon_field] = lon
        return FixResult(dict(mutable), fixes, changes)

    def fix_all(self, rows: Iterable[Mapping[str, Any]]) -> List[FixResult]:
        return [self.fix_record(row) for row in rows]

    def validate_after_fix(self, rows: Iterable[Mapping[str, Any]]) -> List[ValidationIssue]:
        fixed = (result.record for result in self.fix_all(rows))
        return self.validator.validate(fixed)

    def _coerce_value(self, value: Any) -> Tuple[float | None, list[str], bool]:
        # Normalize common string formats (spaces, comma decimals, N/S/E/W suffixes) then cast.
        if value is None:
            return None, [], False
        original = value
        fixes: list[str] = []
        if isinstance(value, str):
            cleaned = value.strip()
            cleaned = cleaned.replace(",", ".")
            if cleaned and cleaned[-1].upper() in {"N", "S", "E", "W"}:
                # Drop the compass letter and flip sign if needed.
                direction = cleaned[-1].upper()
                cleaned = cleaned[:-1]
                try:
                    numeric = float(cleaned)
                    if direction == "S":
                        numeric = -abs(numeric)
                    if direction == "W":
                        numeric = -abs(numeric)
                    if direction in {"N", "E"}:
                        numeric = abs(numeric)
                    value = numeric
                except ValueError:
                    value = cleaned
            else:
                value = cleaned
            fixes.append("coerced_from_string")
        try:
            # Try the final float conversion.
            number = float(value)
            return number, fixes, number != original
        except (TypeError, ValueError):
            fixes.append("coerce_failed")
            return None, fixes, False

    def _looks_swapped(self, lat: float, lon: float) -> bool:
        # Lat in longitude-like range and lon in latitude-like range is a common swap signal.
        return abs(lat) > 90 and abs(lat) <= 180 and abs(lon) <= 90

    def _wrap_longitude(self, lon: float) -> Tuple[float, bool]:
        # Convert 0–360 style longitudes to -180–180 so they can be clipped/validated.
        if -180 <= lon <= 180:
            return lon, False
        if -360 <= lon <= 360:
            wrapped = ((lon + 180) % 360) - 180
            return wrapped, True
        return lon, False

    def _handle_outlier(self, value: float, fallback_value: float) -> Tuple[float, bool]:
        # If max_abs is set, replace extreme spikes with the fallback.
        if self.max_abs is None:
            return value, False
        if abs(value) > self.max_abs:
            return fallback_value, True
        return value, False

    def _clip(self, value: float, lower: float, upper: float) -> float:
        # Simple numeric clamp.
        return min(max(value, lower), upper)
