import pytest

from app.calculator import calculate_productivity
from app.schemas import ExcavatorInput


def make_input(**overrides):
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
        "annual_plan_volume": None,
    }
    data.update(overrides)
    return ExcavatorInput(**data)


def test_hourly_productivity_formula():
    data = make_input(
        bucket_volume=2.5,
        bucket_fill_factor=0.9,
        cycle_time_seconds=45,
    )

    result = calculate_productivity(data)

    assert result.hourly_productivity == pytest.approx(180)


def test_service_count_uses_floor_division():
    data = make_input(service_interval_hours=499)

    result = calculate_productivity(data)

    # 5280 // 499 = 10
    assert result.service_count == 10


def test_no_service_below_first_interval():
    data = make_input(service_interval_hours=6000)

    result = calculate_productivity(data)

    assert result.service_count == 0
    assert result.service_hours == pytest.approx(0)


def test_zero_service_duration_gives_zero_service_hours():
    data = make_input(service_duration_hours=0)

    result = calculate_productivity(data)

    assert result.service_count == 10
    assert result.service_hours == pytest.approx(0)
    assert result.clean_work_hours == pytest.approx(5016)


def test_zero_emergency_downtime():
    data = make_input(emergency_downtime_percent=0)

    result = calculate_productivity(data)

    assert result.emergency_downtime_hours == pytest.approx(0)
    assert result.clean_work_hours == pytest.approx(5180)
    assert result.technical_availability == pytest.approx(5180 / 5280)


def test_clean_work_hours_is_never_negative():
    data = make_input(
        service_interval_hours=10,
        service_duration_hours=100,
        annual_plan_volume=500_000,
    )

    result = calculate_productivity(data)

    assert result.clean_work_hours == pytest.approx(0)
    assert result.technical_availability == pytest.approx(0)
    assert result.annual_productivity == pytest.approx(0)
    assert result.plan_is_completed is False


def test_availability_applied_at_exactly_1000_hours():
    data = make_input(shift_hours=8, shifts_per_day=1, working_days_per_year=125)

    result = calculate_productivity(data)

    assert result.scheduled_work_hours == pytest.approx(1000)
    assert result.service_count == 2
    assert result.clean_work_hours == pytest.approx(930)
    assert result.technical_availability == pytest.approx(0.93)


def test_availability_not_applied_below_1000_hours():
    data = make_input(shift_hours=8, shifts_per_day=1, working_days_per_year=124)

    result = calculate_productivity(data)

    assert result.scheduled_work_hours == pytest.approx(992)
    assert result.emergency_downtime_hours == pytest.approx(0)
    assert result.clean_work_hours == pytest.approx(992)
    assert result.technical_availability == pytest.approx(1)


def test_plan_completion_percent_value():
    data = make_input(annual_plan_volume=294_960)

    result = calculate_productivity(data)

    assert result.plan_completion_percent == pytest.approx(200)
    assert result.plan_is_completed is True


def test_plan_exact_boundary_counts_as_completed():
    data = make_input(annual_plan_volume=589_920)

    result = calculate_productivity(data)

    assert result.plan_completion_percent == pytest.approx(100)
    assert result.plan_is_completed is True


def test_recommendation_suggests_replacement_above_20_percent():
    data = make_input(emergency_downtime_percent=25)

    result = calculate_productivity(data)

    assert "замену машины" in result.recommendation


def test_recommendation_suggests_overhaul_above_10_percent():
    data = make_input(emergency_downtime_percent=15)

    result = calculate_productivity(data)

    assert "капитальный ремонт" in result.recommendation


def test_no_downtime_warning_for_small_workload():
    data = make_input(
        shift_hours=1,
        shifts_per_day=1,
        working_days_per_year=100,
        emergency_downtime_percent=25,
    )

    result = calculate_productivity(data)

    assert result.recommendation == "План не задан."


def test_combined_recommendation_plan_and_downtime():
    data = make_input(
        emergency_downtime_percent=25,
        annual_plan_volume=1_000_000,
    )

    result = calculate_productivity(data)

    assert "недостаточно" in result.recommendation
    assert "замену машины" in result.recommendation
