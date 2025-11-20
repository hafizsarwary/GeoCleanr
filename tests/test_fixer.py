from geocleanr.fixer import CoordinateFixer


def test_coordinate_fixer_swaps_axes_and_clips():
    fixer = CoordinateFixer()
    result = fixer.fix_record({"lat": 200, "lon": 45})

    assert result.record["lat"] == 90
    assert "lat_clipped" in result.fixes

    swapped = fixer.fix_record({"lat": 100, "lon": 25})
    assert swapped.record["lat"] == 25
    assert "swapped_axes" in swapped.fixes


def test_coordinate_fixer_handles_missing_values():
    fixer = CoordinateFixer(fallback=(1.0, 2.0))

    result = fixer.fix_record({"lat": None, "lon": None})

    assert result.record["lat"] == 1.0
    assert "filled_missing" in result.fixes
