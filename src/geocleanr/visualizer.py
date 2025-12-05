from __future__ import annotations

from typing import Iterable, Mapping, Any, List, Tuple


class AsciiHeatmap:
    """
    Render a coarse ASCII heatmap of coordinate density.

    The heatmap is a simple grid where each cell counts how many points
    fall into its latitude/longitude bin, and then uses characters of
    increasing "intensity" to represent density.

    Typical usage:
        heatmap = AsciiHeatmap(rows=6, cols=12)
        text = heatmap.render(records)
        print(text)
    """

    def __init__(
        self,
        rows: int = 6,
        cols: int = 12,
        lat_field: str = "lat",
        lon_field: str = "lon",
        lat_range: Tuple[float, float] = (-90.0, 90.0),
        lon_range: Tuple[float, float] = (-180.0, 180.0),
    ) -> None:
        """
        Args:
            rows: Number of grid rows (vertical bins).
            cols: Number of grid columns (horizontal bins).
            lat_field: Key name for latitude in each record.
            lon_field: Key name for longitude in each record.
            lat_range: Minimum and maximum latitude to visualize.
            lon_range: Minimum and maximum longitude to visualize.
        """
        self.rows = rows
        self.cols = cols
        self.lat_field = lat_field
        self.lon_field = lon_field
        self.lat_min, self.lat_max = lat_range
        self.lon_min, self.lon_max = lon_range

        # Characters from "no data" up to "max density"
        self._chars = ".-+*"

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def render(self, records: Iterable[Mapping[str, Any]]) -> str:
        """
        Build the ASCII heatmap for the given records.

        Args:
            records: An iterable of mapping-like objects (e.g. dicts),
                     each containing at least the latitude and longitude
                     fields configured in the constructor.

        Returns:
            A multiline string representing the heatmap. Each row of the
            string is a line of ASCII characters.
        """
        grid = self._build_grid(records)

        total_points = sum(sum(row) for row in grid)
        if total_points == 0:
            return "(no plottable coordinates)"

        max_count = max(max(row) for row in grid) or 1

        lines: List[str] = []

        # We want "north" (higher latitude) at the top, so we render
        # rows from highest lat (index 0) to lowest (index rows-1)
        for r in range(self.rows):
            row_cells = []
            for c in range(self.cols):
                value = grid[r][c]
                char = self._value_to_char(value, max_count)
                row_cells.append(char)
            lines.append("".join(row_cells))

        # Add a simple legend at the bottom
        lines.append("")
        lines.append("Legend: . = none, - = low, + = medium, * = high density")
        lines.append(
            f"Lat range: [{self.lat_min}, {self.lat_max}], "
            f"Lon range: [{self.lon_min}, {self.lon_max}]"
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _build_grid(self, records: Iterable[Mapping[str, Any]]) -> List[List[int]]:
        """
        Bin all records into a rows x cols grid based on lat/lon.
        """
        # Initialize zero counts
        grid = [[0 for _ in range(self.cols)] for _ in range(self.rows)]

        for record in records:
            lat_raw = record.get(self.lat_field)
            lon_raw = record.get(self.lon_field)

            # Skip records without numeric coordinates
            try:
                lat = float(lat_raw)
                lon = float(lon_raw)
            except (TypeError, ValueError):
                continue

            # Skip coordinates outside the configured ranges
            if not (self.lat_min <= lat <= self.lat_max):
                continue
            if not (self.lon_min <= lon <= self.lon_max):
                continue

            r = self._scale(lat, self.lat_min, self.lat_max, self.rows, invert=True)
            c = self._scale(lon, self.lon_min, self.lon_max, self.cols, invert=False)

            grid[r][c] += 1

        return grid

    def _scale(
        self,
        value: float,
        lower: float,
        upper: float,
        size: int,
        invert: bool = False,
    ) -> int:
        """
        Map a continuous value in [lower, upper] into a grid index [0, size-1].

        If invert=True, higher values map to lower indices (useful for latitudes
        so that larger latitudes appear at the top row).
        """
        span = upper - lower
        if span <= 0:
            # Degenerate range: put everything in the middle row/column
            return size // 2

        normalized = (value - lower) / span  # 0..1

        if invert:
            normalized = 1.0 - normalized

        index = int(normalized * size)
        # Clamp to [0, size-1]
        return max(0, min(size - 1, index))

    def _value_to_char(self, value: int, max_value: int) -> str:
        """
        Convert a cell count into one of the ASCII characters.

        0 -> '.'
        small counts -> '-'
        medium counts -> '+'
        large counts -> '*'
        """
        if value <= 0:
            return self._chars[0]

        ratio = value / max_value

        if ratio > 0.66:
            return self._chars[3]  # '*'
        if ratio > 0.33:
            return self._chars[2]  # '+'
        return self._chars[1]      # '-'
