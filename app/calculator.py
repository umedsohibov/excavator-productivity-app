from app.schemas import ExcavatorInput, ExcavatorResult


def calculate_productivity(data: ExcavatorInput) -> ExcavatorResult:
    hourly_productivity = (
        data.bucket_volume
        * data.bucket_fill_factor
        * 3600
        / data.cycle_time_seconds
    )

    scheduled_work_hours = (
        data.shift_hours
        * data.shifts_per_day
        * data.working_days_per_year
    )

    service_count = (
        int(scheduled_work_hours // data.service_interval_hours)
        if scheduled_work_hours >= data.service_interval_hours
        else 0
    )

    service_hours = service_count * data.service_duration_hours

    apply_technical_availability = scheduled_work_hours >= 1000

    if apply_technical_availability:
        emergency_downtime_hours = (
            scheduled_work_hours
            * data.emergency_downtime_percent
            / 100
        )
        clean_work_hours = scheduled_work_hours - service_hours - emergency_downtime_hours
    else:
        emergency_downtime_hours = 0
        clean_work_hours = scheduled_work_hours

    if clean_work_hours < 0:
        clean_work_hours = 0

    technical_availability = (
        clean_work_hours / scheduled_work_hours
        if scheduled_work_hours > 0
        else 0
    )

    annual_productivity = hourly_productivity * clean_work_hours

    if data.annual_plan_volume is None:
        plan_completion_percent = None
        plan_is_completed = None
    else:
        plan_completion_percent = (
            annual_productivity / data.annual_plan_volume * 100
        )
        plan_is_completed = (
            annual_productivity >= data.annual_plan_volume
        )

    recommendation = build_recommendation(
        plan_is_completed=plan_is_completed,
        emergency_downtime_percent=data.emergency_downtime_percent,
        apply_technical_availability=apply_technical_availability,
    )

    return ExcavatorResult(
        hourly_productivity=hourly_productivity,
        scheduled_work_hours=scheduled_work_hours,
        service_count=service_count,
        service_hours=service_hours,
        emergency_downtime_hours=emergency_downtime_hours,
        clean_work_hours=clean_work_hours,
        technical_availability=technical_availability,
        annual_productivity=annual_productivity,
        plan_completion_percent=plan_completion_percent,
        plan_is_completed=plan_is_completed,
        recommendation=recommendation,
    )

def build_recommendation(
    plan_is_completed: bool | None,
    emergency_downtime_percent: float,
    apply_technical_availability: bool,
) -> str:
    recommendations = []

    if plan_is_completed is True:
        recommendations.append("Производственный план выполняется.")

    if plan_is_completed is False:
        recommendations.append(
            "Производительности недостаточно для выполнения плана. "
            "Требуется изменить параметры техники или режим работы."
        )

    if plan_is_completed is None:
        recommendations.append("План не задан.")

    if apply_technical_availability:
        if emergency_downtime_percent > 20:
            recommendations.append(
                "Аварийные простои превышают 20%. "
                "Рекомендуется рассмотреть замену машины."
            )
        elif emergency_downtime_percent > 10:
            recommendations.append(
                "Аварийные простои превышают 10%. "
                "Рекомендуется запланировать капитальный ремонт."
            )

    return " ".join(recommendations)