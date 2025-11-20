from geocleanr.fixer import CoordinateFixer
from geocleanr.reporter import ReportBuilder
from geocleanr.validator import GeometryValidator


def test_end_to_end_flow_generates_report_and_fixed_records():
    records = [
        {"lat": 95, "lon": 10},
        {"lat": 20, "lon": None},
    ]
    validator = GeometryValidator()
    issues = validator.validate(records)
    assert len(issues) >= 2

    fixer = CoordinateFixer(fallback=(42.0, -71.0))
    fixed_records = [result.record for result in fixer.fix_all(records)]
    assert validator.is_valid(fixed_records)

    builder = ReportBuilder()
    summary = builder.build_summary(issues)
    text = builder.to_markdown(summary)

    assert "Total issues" in text
    assert summary["total_issues"] == len(issues)
