from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping, Dict, Any, List

from .validator import ValidationIssue


class ReportBuilder:
    """
    Builds human-readable summaries and Markdown reports
    from a collection of ValidationIssue objects.

    Typical usage:
        builder = ReportBuilder(sample_size=5)
        summary = builder.build_summary(issues)
        md = builder.to_markdown(summary)
    """

    def __init__(self, sample_size: int = 5) -> None:
        """
        Args:
            sample_size: Maximum number of individual issues to include
                         in the 'sample' section of the report.
        """
        self.sample_size = max(sample_size, 0)

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    def build_summary(self, issues: Iterable[ValidationIssue]) -> Dict[str, Any]:
        """
        Aggregates a list/stream of ValidationIssue objects into a summary.

        The summary contains:
            - 'total_issues': total number of issues
            - 'by_field': counts of issues per field/column
            - 'by_message': counts of issues per message text
            - 'by_code': counts of issues per error code (if available)
            - 'sample': a list of formatted strings for the first N issues

        Args:
            issues: Any iterable of ValidationIssue objects.

        Returns:
            A dictionary with aggregated statistics and samples.
        """
        # Materialize the iterable so we can iterate multiple times
        issues_list: List[ValidationIssue] = list(issues)

        # Basic counts
        total_issues = len(issues_list)
        field_counts = Counter(issue.field for issue in issues_list)
        message_counts = Counter(issue.message for issue in issues_list)

        # Optional: group by 'code' if the ValidationIssue has that attribute
        # (this keeps the code backward-compatible even if 'code' is missing).
        code_counts: Counter[str] = Counter()
        for issue in issues_list:
            code = getattr(issue, "code", None)
            if code is not None:
                code_counts[code] += 1

        # Create a preview of the first N issues
        sample_issues = [
            self._format_issue(issue)
            for issue in issues_list[: self.sample_size]
        ]

        summary: Dict[str, Any] = {
            "total_issues": total_issues,
            "by_field": dict(field_counts),
            "by_message": dict(message_counts),
            # Only include 'by_code' if at least one code was found
            "by_code": dict(code_counts) if code_counts else {},
            "sample": sample_issues,
        }
        return summary

    def to_markdown(self, summary: Mapping[str, Any]) -> str:
        """
        Converts a summary dictionary into a Markdown-formatted report.

        Args:
            summary: A dictionary usually created by build_summary().

        Returns:
            A Markdown string suitable for saving to a .md file
            or printing to the console.
        """
        lines: List[str] = ["# GeoCleanr Validation Report", ""]

        # ------------------------------------------------------------------
        # Section 1: Overall totals
        # ------------------------------------------------------------------
        total = summary.get("total_issues", 0)
        lines.append(f"**Total issues detected:** {total}")
        lines.append("")

        if total == 0:
            lines.append("✅ No validation issues found. Your data looks clean!")
            return "\n".join(lines)

        # ------------------------------------------------------------------
        # Section 2: Issues by field
        # ------------------------------------------------------------------
        lines.append("## Issues by Field")
        by_field: Mapping[str, int] = summary.get("by_field", {})

        if not by_field:
            lines.append("- *No field-level statistics available.*")
        else:
            for field, count in sorted(by_field.items()):
                lines.append(f"- **{field}**: {count} issue(s)")
        lines.append("")

        # ------------------------------------------------------------------
        # Section 3: Issues by message (top few patterns)
        # ------------------------------------------------------------------
        lines.append("## Issues by Message")
        by_message: Mapping[str, int] = summary.get("by_message", {})

        if not by_message:
            lines.append("- *No message-level statistics available.*")
        else:
            # Sort by descending frequency, then message text
            for message, count in sorted(
                by_message.items(), key=lambda kv: (-kv[1], kv[0])
            ):
                lines.append(f"- `{message}` — {count} occurrence(s)")
        lines.append("")

        # ------------------------------------------------------------------
        # Section 4: Issues by error code (if any)
        # ------------------------------------------------------------------
        by_code: Mapping[str, int] = summary.get("by_code", {})
        if by_code:
            lines.append("## Issues by Error Code")
            for code, count in sorted(by_code.items()):
                lines.append(f"- **{code}**: {count} issue(s)")
            lines.append("")

        # ------------------------------------------------------------------
        # Section 5: Sample issues
        # ------------------------------------------------------------------
        lines.append(f"## Sample Issues (first {self.sample_size})")
        sample: List[str] = summary.get("sample", [])

        if not sample:
            lines.append("- *No sample issues available.*")
        else:
            for entry in sample:
                lines.append(f"- {entry}")

        return "\n".join(lines)

    # ----------------------------------------------------------------------
    # Internal helpers
    # ----------------------------------------------------------------------
    def _format_issue(self, issue: ValidationIssue) -> str:
        """
        Formats a single ValidationIssue into a concise human-readable string.
        """
        base = f"Row #{issue.index} [{issue.field}]: {issue.message}"
        code = getattr(issue, "code", None)
        if code is not None:
            return f"{base} (code={code})"
        return base
