console.log("calculate.js loaded fresh");

let benchmarkChart = null;
let co2Chart = null;
let costChart = null;

document.addEventListener("DOMContentLoaded", () => {
    const form = document.getElementById("impactForm");
    const resultCard = document.getElementById("resultCard");

    // Simple / Advanced Toggle Setup
    const simpleToggle = document.getElementById("simpleToggle");
    const advancedToggle = document.getElementById("advancedToggle");
    const advancedFields = document.getElementById("advancedFields");

    // Initial state = Simple active
    simpleToggle.classList.add("active");
    advancedToggle.classList.remove("active");
    advancedFields.style.display = "none";

    // Simple click
    simpleToggle.addEventListener("click", function (e) {
        e.preventDefault();
        simpleToggle.classList.add("active");
        advancedToggle.classList.remove("active");
        advancedFields.style.display = "none";
    });

    // Advanced click
    advancedToggle.addEventListener("click", function (e) {
        e.preventDefault();
        advancedToggle.classList.add("active");
        simpleToggle.classList.remove("active");
        advancedFields.style.display = "block";
    });

    // Fetch regions
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

    // Fetch facility types
    fetch("http://localhost:8000/facility-types")
        .then(response => response.json())
        .then(data => {
            const facilitySelect = document.getElementById("facilityType");
            facilitySelect.innerHTML = '<option value="">-- Select Facility type --</option>';
            data.facility_types.forEach(type => {
                const option = document.createElement("option");
                option.value = type;
                option.textContent = type.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
                facilitySelect.appendChild(option);
            });
        })
        .catch(error => {
            console.error("Failed to load facility types:", error);
            document.getElementById("facilityType").innerHTML = '<option value="">-- Failed to load types --</option>';
        });

    // FORM SUBMIT HANDLER
    form.addEventListener("submit", async (event) => {
        event.preventDefault();

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
                    const message = error.map(e => `• ${e.loc.join(".")}: ${e.msg}`).join("\n");
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

            // Clear old charts
            [benchmarkChart, co2Chart, costChart].forEach(chart => {
                if (chart !== null) chart.destroy();
            });
            benchmarkChart = co2Chart = costChart = null;

            // Chart: kWh
            if (benchmarkData?.target_kwh !== null) {
                const ctx = document.getElementById("benchmarkChart").getContext("2d");
                benchmarkChart = renderBarChart(ctx, "kWh/year", benchmarkData.target_kwh, result.estimated_kwh, "Energy Usage (kWh/year)", "kWh");
            }

            // Chart: CO2
            if (benchmarkData?.target_co2 !== null) {
                const co2Ctx = document.getElementById("co2Chart").getContext("2d");
                co2Chart = renderBarChart(co2Ctx, "CO₂ (kg/year)", benchmarkData.target_co2, result.estimated_co2_kg, "CO₂ Emissions (kg/year)", "kg");
            }

            // Chart: Cost
            if (benchmarkData?.target_cost !== null) {
                const costCtx = document.getElementById("costChart").getContext("2d");
                costChart = renderBarChart(costCtx, "NOK/year", benchmarkData.target_cost, result.estimated_cost_nok, "Energy Cost (NOK/year)", "NOK");
            }

            // Tooltips
            if (meta.estimated_baseline_kwh !== undefined && meta.size_multiplier !== undefined) {
                document.getElementById("usageInfo").title =
                    `Estimated using baseline (${meta.estimated_baseline_kwh.toLocaleString()} kWh) × multiplier (${meta.size_multiplier}) = ${result.estimated_kwh.toLocaleString()} kWh`;
            } else {
                document.getElementById("usageInfo").title =
                    `Custom usage provided: ${result.estimated_kwh.toLocaleString()} kWh`;
            }

            document.getElementById("emissionsInfo").title =
                `CO₂ = ${result.estimated_kwh.toLocaleString()} kWh × ${meta.emission_factor_used} kg/kWh = ${result.estimated_co2_kg.toLocaleString()} kg`;

            document.getElementById("costPerYearInfo").title =
                `Base price: ${meta.raw_price} + grid fee: ${meta.grid_fee_added} ${meta.is_vat_exempt ? "(VAT exempt)" : "+ 25% VAT"} = final: ${meta.final_price} NOK/kWh, adjusted for ${meta.industry_class} (×${meta.industry_modifier})`;

            document.getElementById("resultKwh").innerText = result.estimated_kwh.toLocaleString();
            document.getElementById("resultCo2").innerText = result.estimated_co2_kg.toLocaleString();
            document.getElementById("resultCost").innerText = result.estimated_cost_nok.toLocaleString();

            resultCard.classList.remove("inactive");

        } catch (err) {
            console.error("Error contacting backend:", err);
            alert("Could not connect to backend.");
        }
    });

    // Chart rendering helper
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
});
