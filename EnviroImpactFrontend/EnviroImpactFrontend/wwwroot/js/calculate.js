console.log("calculate.js loaded fresh");

let benchmarkChart = null;
let co2Chart = null;
let costChart = null;

let lastResult = null;
let lastMeta = null;
let timeFrame = "year"; // Default

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("impactForm");
    const resultCard = document.getElementById("resultCard");
    const loadingStatus = document.getElementById("loadingStatus");
    const submitButton = form.querySelector('button[type="submit"]');
    const timeFrameSelector = document.getElementById("timeFrameSelector");

    const simpleToggle = document.getElementById("simpleToggle");
    const advancedToggle = document.getElementById("advancedToggle");
    const advancedFields = document.getElementById("advancedFields");

    simpleToggle.classList.add("active");
    advancedToggle.classList.remove("active");
    advancedFields.style.display = "none";

    simpleToggle.addEventListener("click", function (e) {
        e.preventDefault();
        simpleToggle.classList.add("active");
        advancedToggle.classList.remove("active");
        advancedFields.style.display = "none";
    });

    advancedToggle.addEventListener("click", function (e) {
        e.preventDefault();
        advancedToggle.classList.add("active");
        simpleToggle.classList.remove("active");
        advancedFields.style.display = "block";
    });

    fetch("http://localhost:8000/regions")
        .then(response => response.json())
        .then(data => {
            const regionSelect = document.getElementById("location");
            regionSelect.innerHTML = '<option value="">-- Select Region --</option>';
            data.regions.forEach(region => {
                const option = document.createElement("option");
                option.value = region;
                option.textContent = region;
                regionSelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Failed to load regions:", error);
            document.getElementById("location").innerHTML = '<option value="">-- Failed to load regions --</option>';
        });

    fetch("http://localhost:8000/facility-types")
        .then(response => response.json())
        .then(data => {
            const facilitySelect = document.getElementById("facilityType");
            facilitySelect.innerHTML = '<option value="">-- Select Facility type --</option>';
            data.facility_types.forEach(type => {
                const option = document.createElement("option");
                option.value = type;
                option.textContent = type.replace(/_/g, " ").replace(/\w/g, l => l.toUpperCase());
                facilitySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Failed to load facility types:", error);
            document.getElementById("facilityType").innerHTML = '<option value="">-- Failed to load types --</option>';
        });

    form.addEventListener("submit", async (event) => {
        event.preventDefault();
        submitButton.disabled = true;
        loadingStatus.style.display = "block";
        resultCard.classList.add("inactive");

        const data = {
            region: document.getElementById("location").value,
            facility_type: document.getElementById("facilityType").value,
            size: document.getElementById("size").value,
            custom_kwh: parseFloat(document.getElementById("customKwh").value) || null,
            usage_pattern: document.getElementById("usagePattern").value,
            custom_emission_factor: parseFloat(document.getElementById("customEmission").value) || null,
            custom_price_per_kwh: parseFloat(document.getElementById("customPrice").value) || null
        };

        try {
            const response = await fetch("http://localhost:8000/calculate", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(data)
            });

            if (!response.ok) {
                const error = await response.json();
                if (Array.isArray(error)) {
                    const message = error.map(e => `��� ${e.loc.join(".")}: ${e.msg}`).join("\n");
                    alert("Validation Errors:\n" + message);
                } else if (error.detail) {
                    alert("Error: " + error.detail);
                } else {
                    alert("Unexpected error:\n" + JSON.stringify(error, null, 2));
                }
                return;
            }

            const result = await response.json();
            const meta = result.metadata;
            const benchmarkData = meta.best_practice_target;

            lastResult = result;
            lastMeta = meta;

            [benchmarkChart, co2Chart, costChart].forEach(chart => {
                if (chart !== null) chart.destroy();
            });
            benchmarkChart = co2Chart = costChart = null;

            if (benchmarkData?.target_kwh !== null) {
                const ctx = document.getElementById("benchmarkChart").getContext("2d");
                benchmarkChart = renderBarChart(ctx, "kWh/year", benchmarkData.target_kwh, result.estimated_kwh, "Energy Usage (kWh/year)", "kWh");
            }

            if (benchmarkData?.target_co2 !== null) {
                const co2Ctx = document.getElementById("co2Chart").getContext("2d");
                co2Chart = renderBarChart(co2Ctx, "CO��� (kg/year)", benchmarkData.target_co2, result.estimated_co2_kg, "CO��� Emissions (kg/year)", "kg");
            }

            if (benchmarkData?.target_cost !== null) {
                const costCtx = document.getElementById("costChart").getContext("2d");
                costChart = renderBarChart(costCtx, "NOK/year", benchmarkData.target_cost, result.estimated_cost_nok, "Energy Cost (NOK/year)", "NOK");
            }

            updateResultDisplay(timeFrame === "month" ? 1 / 12 : 1);
            submitButton.disabled = false;
            loadingStatus.style.display = "none";
            resultCard.classList.remove("inactive");

        } catch (err) {
            submitButton.disabled = false;
            loadingStatus.style.display = "none";
            resultCard.classList.add("inactive");
            console.error("Error contacting backend:", err);
            alert("Could not connect to backend.");
        }
    });

    timeFrameSelector.addEventListener("change", () => {
        timeFrame = timeFrameSelector.value;
        const scaling = timeFrame === "month" ? 1 / 12 : 1;
        updateResultDisplay(scaling);
    });
});

function updateResultDisplay(scaling) {
    if (!lastResult || !lastMeta) return;

    const result = lastResult;
    const meta = lastMeta;

    const scaledKwh = result.estimated_kwh * scaling;
    const scaledCo2 = result.estimated_co2_kg * scaling;
    const scaledCost = result.estimated_cost_nok * scaling;

    document.getElementById("resultKwh").innerText = scaledKwh.toLocaleString(undefined, { maximumFractionDigits: 1 });
    document.getElementById("resultCo2").innerText = scaledCo2.toLocaleString(undefined, { maximumFractionDigits: 2 });
    document.getElementById("resultCost").innerText = scaledCost.toLocaleString(undefined, { maximumFractionDigits: 2 });

    document.querySelector("h5:has(#usageInfo)").innerHTML = `Usage per ${timeFrame} <i id="usageInfo" class="bi bi-info-circle ms-2 text-secondary" data-bs-toggle="tooltip" title=""></i>`;
    document.querySelector("h5:has(#emissionsInfo)").innerHTML = `Emissions per ${timeFrame} <i id="emissionsInfo" class="bi bi-info-circle ms-2 text-secondary" data-bs-toggle="tooltip" title=""></i>`;
    document.querySelector("h5:has(#costPerYearInfo)").innerHTML = `Cost per ${timeFrame} <i id="costPerYearInfo" class="bi bi-info-circle ms-2 text-secondary" data-bs-toggle="tooltip" title=""></i>`;

    const usageInfo = document.getElementById("usageInfo");
    const emissionsInfo = document.getElementById("emissionsInfo");
    const costInfo = document.getElementById("costPerYearInfo");

    if (meta.estimated_baseline_kwh !== undefined && meta.size_multiplier !== undefined) {
        usageInfo.title = `Estimated using baseline (${meta.estimated_baseline_kwh.toLocaleString()} kWh) �� multiplier (${meta.size_multiplier}) �� scale (${scaling})`;
    } else {
        usageInfo.title = `Custom usage scaled for selected time frame (${scaling})`;
    }

    emissionsInfo.title = `CO��� = ${scaledKwh.toLocaleString()} kWh �� ${meta.emission_factor_used} kg/kWh = ${scaledCo2.toLocaleString()} kg`;
    costInfo.title = `Base price: ${meta.raw_price} + grid fee: ${meta.grid_fee_added} ${meta.is_vat_exempt ? "(VAT exempt)" : "+ 25% VAT"} = final: ${meta.final_price} NOK/kWh, adjusted �� ${meta.industry_modifier}, scaled by ${scaling}`;

    document.querySelectorAll('[data-bs-toggle="tooltip"]').forEach(el => new bootstrap.Tooltip(el));
}

function renderBarChart(ctx, label, benchmarkValue, actualValue, yTitle, unit) {
    return new Chart(ctx, {
        type: "bar",
        data: {
            labels: ["Best Practice Target", "Your Facility"],
            datasets: [{
                label: label,
                data: [benchmarkValue, actualValue],
                backgroundColor: ["rgba(54, 162, 235, 0.7)", "rgba(255, 99, 132, 0.7)"],
                borderColor: ["rgba(54, 162, 235, 1)", "rgba(255, 99, 132, 1)"],
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            scales: {
                y: {
                    beginAtZero: true,
                    title: { display: true, text: yTitle }
                }
            },
            plugins: {
                legend: { display: false },
                tooltip: {
                    callbacks: {
                        label: function (context) {
                            return `${context.dataset.label}: ${context.parsed.y.toLocaleString()} ${unit}`;
                        }
                    }
                }
            }
        }
    });
}