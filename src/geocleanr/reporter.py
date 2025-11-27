from __future__ import annotations

from collections import Counter
from typing import Iterable, Mapping, List, Dict, Any

# Assuming ValidationIssue is defined in .validator
# If it's not imported correctly, make sure the file structure is right.
from .validator import ValidationIssue


class ReportBuilder:
    """Generates human-readable summaries of geospatial data validation.

    This class takes the raw error data found by the Validator and transforms
    it into statistical summaries and formatted reports (Markdown).
    """

    def build_summary(self, issues: Iterable[ValidationIssue]) -> Dict[str, Any]:
        """Aggregates a list of validation errors into a statistical summary.

        It iterates through the provided issues to calculate total error counts,
        groups them by the field (column) where they occurred, and extracts a 
        small sample of specific error messages for review.

        Args:
            issues (Iterable[ValidationIssue]): A stream or list of error objects 
                detected by the validator module. Each object must have 'field', 
                'index', and 'message' attributes.

        Returns:
            Dict[str, Any]: A dictionary containing:
                - 'total_issues' (int): The total count of errors found.
                - 'by_field' (dict): Counts of errors grouped by column name.
                - 'sample' (list): A list of formatted strings representing the 
                  first 5 errors found.
        """
        # Convert the iterable to a list so we can iterate over it multiple times
        # (e.g., once for counting, once for sampling)
        issues_list = list(issues)

        # Count occurrences of errors in each specific column/field using a generator expression
        field_counts = Counter(issue.field for issue in issues_list)

        # Construct the summary dictionary
        summary = {
            "total_issues": len(issues_list),
            "by_field": dict(field_counts),
            # Create a readable string for the first 5 issues to serve as a preview
            "sample": [
                f"Row #{issue.index} [{issue.field}]: {issue.message}"
                for issue in issues_list[:5]
            ],
        }
        return summary

    def to_markdown(self, summary: Mapping[str, Any]) -> str:
        """Converts a summary dictionary into a Markdown formatted report string.

        Args:
            summary (Mapping[str, Any]): The dictionary returned by build_summary().
                Must contain keys: 'total_issues', 'by_field', and 'sample'.

        Returns:
            str: A multi-line string formatted in Markdown, ready to be saved 
            as a .md file or printed to the console.
        """
        lines = ["# GeoCleanr Report", ""]
        
        # Section 1: High-level totals
        lines.append(f"**Total issues detected:** {summary.get('total_issues', 0)}")
        lines.append("")

        # Section 2: Breakdown by Field
        lines.append("## Issues by Field")
        by_field = summary.get("by_field", {})
        
        if not by_field:
            lines.append("- *No issues detected.*")
        else:
            # Sort fields alphabetically for a cleaner report
            for field, count in sorted(by_field.items()):
                lines.append(f"- **{field}**: {count} issues")
        
        lines.append("")

        # Section 3: Sample Errors
        lines.append("## Error Samples (First 5)")
        sample = summary.get("sample", [])
        
        if not sample:
            lines.append("- Validation passed for all records.")
        else:
            for entry in sample:
                lines.append(f"- {entry}")

        # Join all lines with newline characters to form the final document
        return "\n".join(lines)