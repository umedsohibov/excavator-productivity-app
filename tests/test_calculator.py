import pytest

from app.calculator import calculate_productivity
from app.schemas import ExcavatorInput


def test_calculate_productivity_with_completed_plan():
    data = ExcavatorInput(
        bucket_volume=1,
        bucket_fill_factor=1,
        cycle_time_seconds=30,
        shift_hours=8,
        shifts_per_day=2,
        working_days_per_year=330,
        service_interval_hours=500,
        service_duration_hours=10,
        emergency_downtime_percent=5,
        annual_plan_volume=500_000,
    )

    result = calculate_productivity(data)

    assert result.hourly_productivity == pytest.approx(120)
    assert result.scheduled_work_hours == pytest.approx(5280)
    assert result.service_count == 10
    assert result.service_hours == pytest.approx(100)
    assert result.emergency_downtime_hours == pytest.approx(264)
    assert result.clean_work_hours == pytest.approx(4916)
    assert result.technical_availability == pytest.approx(0.931, rel=0.001)
    assert result.annual_productivity == pytest.approx(589_920)
    assert result.plan_is_completed is True


def test_calculate_productivity_without_plan():
    data = ExcavatorInput(
        bucket_volume=1,
        bucket_fill_factor=1,
        cycle_time_seconds=30,
        shift_hours=8,
        shifts_per_day=2,
        working_days_per_year=330,
        service_interval_hours=500,
        service_duration_hours=10,
        emergency_downtime_percent=5,
        annual_plan_volume=None,
    )

    result = calculate_productivity(data)

    assert result.plan_completion_percent is None
    assert result.plan_is_completed is None
    assert result.recommendation == "План не задан."


def test_calculate_productivity_with_uncompleted_plan():
    data = ExcavatorInput(
        bucket_volume=1,
        bucket_fill_factor=1,
        cycle_time_seconds=30,
        shift_hours=8,
        shifts_per_day=2,
        working_days_per_year=330,
        service_interval_hours=500,
        service_duration_hours=10,
        emergency_downtime_percent=5,
        annual_plan_volume=1_000_000,
    )

    result = calculate_productivity(data)

    assert result.plan_is_completed is False
    assert "недостаточно" in result.recommendation


def test_small_workload_does_not_apply_technical_availability():
    data = ExcavatorInput(
        bucket_volume=1,
        bucket_fill_factor=1,
        cycle_time_seconds=30,
        shift_hours=1,
        shifts_per_day=1,
        working_days_per_year=100,
        service_interval_hours=500,
        service_duration_hours=10,
        emergency_downtime_percent=5,
        annual_plan_volume=None,
    )

    result = calculate_productivity(data)

    assert result.scheduled_work_hours == pytest.approx(100)
    assert result.service_count == 0
    assert result.service_hours == pytest.approx(0)
    assert result.emergency_downtime_hours == pytest.approx(0)
    assert result.clean_work_hours == pytest.approx(100)
    assert result.technical_availability == pytest.approx(1)
    assert result.annual_productivity == pytest.approx(12_000)


def test_invalid_input_raises_validation_error():
    with pytest.raises(Exception):
        ExcavatorInput(
            bucket_volume=0,
            bucket_fill_factor=1,
            cycle_time_seconds=30,
            shift_hours=8,
            shifts_per_day=2,
            working_days_per_year=330,
            service_interval_hours=500,
            service_duration_hours=10,
            emergency_downtime_percent=5,
            annual_plan_volume=500_000,
        )