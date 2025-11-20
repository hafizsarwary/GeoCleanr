import pytest

from geocleanr.validator import GeometryValidator


def test_validator_detects_missing_and_range_errors():
    rows = [
        {"lat": None, "lon": 10},
        {"lat": 95, "lon": 200},
    ]
    validator = GeometryValidator()

    issues = validator.validate(rows)

    assert len(issues) == 3
    assert issues[0].field == "coordinates"
    assert any(issue.field == "lat" for issue in issues)
    assert any(issue.field == "lon" for issue in issues)


def test_validator_precision_rule():
    rows = [{"lat": 10.1, "lon": 20.12}]
    validator = GeometryValidator(precision=2)

    assert validator.validate(rows)[0].field == "precision"
    assert validator.is_valid([])
