import pytest
from pydantic import ValidationError

from app.schemas import ExcavatorInput


def make_valid_input(**overrides):
    data = {
        "bucket_volume": 1,
        "bucket_fill_factor": 1,
        "cycle_time_seconds": 30,
        "shift_hours": 8,
        "shifts_per_day": 2,
        "working_days_per_year": 330,
        "service_interval_hours": 500,
        "service_duration_hours": 10,
        "emergency_downtime_percent": 5,
        "annual_plan_volume": 500_000,
    }
    data.update(overrides)
    return ExcavatorInput(**data)


def test_valid_input_is_accepted():
    data = make_valid_input()

    assert data.bucket_volume == 1
    assert data.annual_plan_volume == 500_000


def test_annual_plan_volume_is_optional_and_defaults_to_none():
    data = {
        "bucket_volume": 1,
        "bucket_fill_factor": 1,
        "cycle_time_seconds": 30,
        "shift_hours": 8,
        "shifts_per_day": 2,
        "working_days_per_year": 330,
        "service_interval_hours": 500,
        "service_duration_hours": 10,
        "emergency_downtime_percent": 5,
    }

    result = ExcavatorInput(**data)

    assert result.annual_plan_volume is None


def test_zero_bucket_volume_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(bucket_volume=0)


def test_negative_cycle_time_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(cycle_time_seconds=-30)


def test_bucket_fill_factor_above_limit_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(bucket_fill_factor=1.6)


def test_shift_hours_above_24_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(shift_hours=25)


def test_shifts_per_day_above_4_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(shifts_per_day=5)


def test_working_days_above_366_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(working_days_per_year=367)


def test_emergency_downtime_percent_above_100_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(emergency_downtime_percent=101)


def test_negative_annual_plan_volume_is_rejected():
    with pytest.raises(ValidationError):
        make_valid_input(annual_plan_volume=-1)
