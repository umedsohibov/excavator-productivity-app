from pydantic import BaseModel, Field


class ExcavatorInput(BaseModel):
    bucket_volume: float = Field(gt=0)
    bucket_fill_factor: float = Field(gt=0, le=1.5)
    cycle_time_seconds: float = Field(gt=0)

    shift_hours: float = Field(gt=0, le=24)
    shifts_per_day: int = Field(gt=0, le=4)
    working_days_per_year: int = Field(gt=0, le=366)

    service_interval_hours: float = Field(gt=0)
    service_duration_hours: float = Field(ge=0)
    emergency_downtime_percent: float = Field(ge=0, le=100)

    annual_plan_volume: float | None = Field(default=None, gt=0)


class ExcavatorResult(BaseModel):
    hourly_productivity: float
    scheduled_work_hours: float
    service_count: int
    service_hours: float
    emergency_downtime_hours: float
    clean_work_hours: float
    technical_availability: float
    annual_productivity: float
    plan_completion_percent: float | None
    plan_is_completed: bool | None
    recommendation: str