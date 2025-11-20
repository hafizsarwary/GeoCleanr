# GeoCleanr quickstart

This walkthrough cleans a synthetic CSV file containing broken coordinates.

1. Create a CSV file:
   ```csv
   lat,lon
   95,10
   20,
   -45,-190
   ```
2. Run the CLI:
   ```bash
   python -m geocleanr.cli --input sample.csv --format csv --report report.md --write-fixed fixed.ndjson --heatmap
   ```
3. Inspect `report.md` for details and open `fixed.ndjson` to see corrected records.
4. To embed GeoCleanr into a notebook, import `GeometryValidator` and `CoordinateFixer` from `geocleanr` and operate on dictionaries or pandas rows.
