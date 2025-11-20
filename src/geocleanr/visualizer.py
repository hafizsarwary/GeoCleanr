from __future__ import annotations

from typing import Iterable, Mapping, Any, List


class AsciiHeatmap:
    """Render a coarse ASCII heatmap of coordinate density."""

    def __init__(self, rows: int = 5, cols: int = 10, lat_field: str = "lat", lon_field: str = "lon") -> None:
        self.rows = rows
        self.cols = cols
        self.lat_field = lat_field
        self.lon_field = lon_field

    def render(self, records: Iterable[Mapping[str, Any]]) -> str:
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]
        total = 0
        for record in records:
            lat = record.get(self.lat_field)
            lon = record.get(self.lon_field)
            try:
                lat_f = float(lat)
                lon_f = float(lon)
            except (TypeError, ValueError):
                continue
            if not (-90 <= lat_f <= 90 and -180 <= lon_f <= 180):
                continue
            r = self._scale(lat_f, -90, 90, self.rows)
            c = self._scale(lon_f, -180, 180, self.cols)
            grid[r][c] += 1
            total += 1
        if total == 0:
            return "(no plottable coordinates)"
        max_count = max(max(row) for row in grid) or 1
        lines: List[str] = []
        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                value = grid[r][c]
                if value == 0:
                    row_cells.append(".")
                else:
                    ratio = value / max_count
                    row_cells.append("*" if ratio > 0.66 else "+" if ratio > 0.33 else "-")
            lines.append("".join(row_cells))
        return "\n".join(lines)

    def _scale(self, value: float, lower: float, upper: float, size: int) -> int:
        span = upper - lower
        normalized = (value - lower) / span
        index = int(normalized * size)
        return min(max(index, 0), size - 1)
