from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping

from .validator import ValidationIssue


class ReportBuilder:
    """Aggregate validation issues into simple summaries."""

    def build_summary(self, issues: Iterable[ValidationIssue]) -> dict:
        issues = list(issues)
        field_counts = Counter(issue.field for issue in issues)
        summary = {
            "total_issues": len(issues),
            "by_field": dict(field_counts),
            "sample": [f"#{issue.index} {issue.field}: {issue.message}" for issue in issues[:5]],
        }
        return summary

    def to_markdown(self, summary: Mapping[str, object]) -> str:
        lines = ["# GeoCleanr Report", ""]
        lines.append(f"Total issues: {summary.get('total_issues', 0)}")
        lines.append("")
        lines.append("## By field")
        by_field = summary.get("by_field", {})
        if not by_field:
            lines.append("- No issues detected")
        else:
            for field, count in by_field.items():
                lines.append(f"- **{field}**: {count}")
        lines.append("")
        lines.append("## Sample")
        sample = summary.get("sample", [])
        if not sample:
            lines.append("- Validation passed for all records")
        else:
            for entry in sample:
                lines.append(f"- {entry}")
        return "\n".join(lines)
