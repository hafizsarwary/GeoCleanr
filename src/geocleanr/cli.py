from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path
from typing import Iterable, Iterator, Mapping

from .validator import GeometryValidator
from .fixer import CoordinateFixer
from .reporter import ReportBuilder
from .visualizer import AsciiHeatmap


def read_csv(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            yield row


def read_ndjson(path: Path) -> Iterator[dict]:
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            line = line.strip()
            if not line:
                continue
            yield json.loads(line)


def write_ndjson(path: Path, rows: Iterable[Mapping[str, object]]) -> None:
    with path.open("w", encoding="utf-8") as handle:
        for row in rows:
            handle.write(json.dumps(row))
            handle.write("\n")


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(description="GeoCleanr command line interface")
    parser.add_argument("--input", required=True, help="Path to CSV or newline-delimited JSON file")
    parser.add_argument("--format", choices=["csv", "ndjson"], default="csv")
    parser.add_argument("--report", help="Path to write Markdown report (defaults to stdout)")
    parser.add_argument("--write-fixed", help="Optional path to write cleaned records as NDJSON")
    parser.add_argument("--heatmap", action="store_true", help="Print ASCII heatmap after validation")
    args = parser.parse_args(argv)

    input_path = Path(args.input)
    if args.format == "csv":
        records = list(read_csv(input_path))
    else:
        records = list(read_ndjson(input_path))

    validator = GeometryValidator()
    fixer = CoordinateFixer()
    builder = ReportBuilder()
    heatmap = AsciiHeatmap()

    issues = validator.validate(records)
    summary = builder.build_summary(issues)
    report_text = builder.to_markdown(summary)

    if args.report:
        Path(args.report).write_text(report_text, encoding="utf-8")
    else:
        print(report_text)

    if args.heatmap:
        visualization = heatmap.render(records)
        print("\nASCII heatmap:\n")
        print(visualization)

    if args.write_fixed:
        fixed = [fixer.fix_record(row).record for row in records]
        write_ndjson(Path(args.write_fixed), fixed)


if __name__ == "__main__":  # pragma: no cover
    main()
