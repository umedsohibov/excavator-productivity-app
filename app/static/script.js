const calculateButton = document.getElementById("calculate_button");
const errorBox = document.getElementById("error_box");

calculateButton.addEventListener("click", async () => {
    errorBox.textContent = "";

    const payload = {
        bucket_volume: Number(document.getElementById("bucket_volume").value),
        bucket_fill_factor: Number(document.getElementById("bucket_fill_factor").value),
        cycle_time_seconds: Number(document.getElementById("cycle_time_seconds").value),

        shift_hours: Number(document.getElementById("shift_hours").value),
        shifts_per_day: Number(document.getElementById("shifts_per_day").value),
        working_days_per_year: Number(document.getElementById("working_days_per_year").value),

        service_interval_hours: Number(document.getElementById("service_interval_hours").value),
        service_duration_hours: Number(document.getElementById("service_duration_hours").value),
        emergency_downtime_percent: Number(document.getElementById("emergency_downtime_percent").value),

        annual_plan_volume: document.getElementById("annual_plan_volume").value
    ? Number(document.getElementById("annual_plan_volume").value)
    : null
    };

    try {
        const response = await fetch("/calculate", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify(payload)
        });

        if (!response.ok) {
            throw new Error("Проверьте корректность введенных данных.");
        }

        const result = await response.json();

        updateResults(result);
    } catch (error) {
        errorBox.textContent = error.message;
    }
});


function updateResults(result) {
    document.getElementById("hourly_productivity").textContent =
        formatNumber(result.hourly_productivity) + " м³/ч";

    document.getElementById("scheduled_work_hours").textContent =
        formatNumber(result.scheduled_work_hours) + " ч";

    document.getElementById("service_count").textContent =
        result.service_count;

    document.getElementById("service_hours").textContent =
        formatNumber(result.service_hours) + " ч";

    document.getElementById("emergency_downtime_hours").textContent =
        formatNumber(result.emergency_downtime_hours) + " ч";

    document.getElementById("clean_work_hours").textContent =
        formatNumber(result.clean_work_hours) + " ч";

    document.getElementById("technical_availability").textContent =
        result.technical_availability.toFixed(3);

    document.getElementById("annual_productivity").textContent =
        formatNumber(result.annual_productivity) + " м³";

    document.getElementById("plan_completion_percent").textContent =
    result.plan_completion_percent !== null
        ? formatNumber(result.plan_completion_percent) + " %"
        : "План не задан";

    document.getElementById("recommendation").textContent =
        result.recommendation;
}


function formatNumber(value) {
    return Number(value).toLocaleString("ru-RU", {
        maximumFractionDigits: 2
    });
}