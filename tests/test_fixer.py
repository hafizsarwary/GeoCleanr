from geocleanr.fixer import CoordinateFixer


def test_coordinate_fixer_swaps_axes_and_clips():
    # Lat is too large, so it will be clipped to 90.
    fixer = CoordinateFixer()
    result = fixer.fix_record({"lat": 200, "lon": 45})

    assert result.record["lat"] == 90
    assert "lat_clipped" in result.fixes

    # Values also look swapped, so lat/lon are flipped.
    swapped = fixer.fix_record({"lat": 100, "lon": 25})
    assert swapped.record["lat"] == 25
    assert "swapped_axes" in swapped.fixes


def test_coordinate_fixer_handles_missing_values():
    # Both values missing: use the fallback pair.
    fixer = CoordinateFixer(fallback=(1.0, 2.0))

    result = fixer.fix_record({"lat": None, "lon": None})

    assert result.record["lat"] == 1.0
    assert "filled_missing" in result.fixes


def test_coordinate_fixer_fills_only_missing_side():
    # Only one side is missing: keep the good value, fill the empty one.
    fixer = CoordinateFixer(fallback=(9.0, 8.0))
    result = fixer.fix_record({"lat": None, "lon": 50})

    assert result.record["lat"] == 9.0
    assert result.record["lon"] == 50
    assert "lat_filled" in result.fixes


def test_coordinate_fixer_coerces_strings_and_wraps_longitude():
    # Trim whitespace, accept comma decimals, wrap 350 to -10.
    fixer = CoordinateFixer()
    result = fixer.fix_record({"lat": " 12,5 ", "lon": 350})

    assert result.record["lat"] == 12.5
    assert result.record["lon"] == -10
    assert "coerced_from_string" in result.fixes
    assert "lon_wrapped" in result.fixes


def test_coordinate_fixer_outlier_guard_and_swap():
    # Swap when lat is in longitude-like range; drop extreme outlier.
    fixer = CoordinateFixer(max_abs=500, fallback=(1.0, 2.0))
    result = fixer.fix_record({"lat": 120, "lon": 40})
    assert result.record["lat"] == 40
    assert "swapped_axes" in result.fixes

    outlier = fixer.fix_record({"lat": 1000, "lon": 10})
    assert outlier.record["lat"] == 1.0
    assert "lat_outlier" in outlier.fixes
