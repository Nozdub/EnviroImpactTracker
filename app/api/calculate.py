from fastapi import APIRouter, HTTPException
from app.models.calculation_input import CalculationInput
from app.services.config_loader import load_static_config
import asyncio
from app.services.electricity_price_api import fetch_average_price
from app.services.benchmark_loader import load_benchmark_data
from app.services.emission_api import fetch_emission_factor

router = APIRouter()

@router.post("/calculate")
def calculate(input_data: CalculationInput):
    config = load_static_config()
    benchmark = load_benchmark_data()

    baseline = None
    multiplier = None

    # Check region
    if input_data.region not in config["regions"]:
        raise HTTPException(status_code=400, detail=f"Invalid region: {input_data.region}")

    # Check facility type
    facility_data = config["facility_types"].get(input_data.facility_type)
    if not facility_data:
        raise HTTPException(status_code=400, detail=f"Invalid facility type: {input_data.facility_type}")

    # Check size
    if input_data.size not in facility_data["size_multipliers"]:
        raise HTTPException(status_code=400, detail=f"Invalid size: {input_data.size}")

    # Determine baseline kWh
    if input_data.custom_kwh is not None:
        estimated_kwh = float(input_data.custom_kwh)
        print(f"[DEBUG] Using custom kWh: {estimated_kwh}")
    else:
        baseline = facility_data["baseline_kwh"]
        multiplier = facility_data["size_multipliers"][input_data.size]
        estimated_kwh = baseline * multiplier
        print(f"[DEBUG] Using baseline kWh: {baseline}")
        print(f"[DEBUG] Size multiplier: {multiplier}")
        print(f"[DEBUG] Estimated kWh (baseline × multiplier): {estimated_kwh}")

    # Applying usage pattern modifiers
    pattern_modifiers = {
        "constant": {"kwh": 1.0, "co2": 1.0, "cost": 1.0},
        "intermittent": {"kwh": 0.5, "co2": 0.95, "cost": 0.95},
        "peak": {"kwh": 1.0, "co2": 1.05, "cost": 1.2}
    }

    pattern = getattr(input_data, "usage_pattern", "constant")
    mod = pattern_modifiers.get(pattern, pattern_modifiers["constant"])

    estimated_kwh *= mod["kwh"]
    print(f"[DEBUG] Applied usage pattern modifiers ({pattern}): kwh modifier {mod['kwh']}")

    # Emission calculation
    if input_data.custom_emission_factor is not None:
        emission_factor = input_data.custom_emission_factor
        emission_timestamp = None
        print(f"[DEBUG] Using custom emission factor: {emission_factor}")
    else:
        try:
            emission_factor, emission_timestamp = asyncio.run(fetch_emission_factor())
            print(f"[DEBUG] Using API emission factor: {emission_factor} at {emission_timestamp}")
        except Exception:
            emission_factor = config["emission_factors"]["default"]
            emission_timestamp = None
            print(f"[DEBUG] Fallback emission factor from config: {emission_factor}")

    estimated_co2_kg = estimated_kwh * emission_factor
    print(f"[DEBUG] Emission factor used: {emission_factor}")
    print(f"[DEBUG] Estimated CO₂ (kWh × factor): {estimated_co2_kg}")

    # Best Practice Target comparison
    bench_entry = benchmark.get(input_data.facility_type, {}).get(input_data.size)
    bench_kwh = None
    percent_above_benchmark = None
    bench_co2 = None
    co2_percent = None
    bench_cost = None
    cost_percent = None

    if bench_entry:
        bench_kwh = bench_entry.get("kwh")
        if bench_kwh:
            percent_above_benchmark = ((estimated_kwh - bench_kwh) / bench_kwh) * 100
            print(f"[DEBUG] Best Practice Target kWh: {bench_kwh}")
            print(f"[DEBUG] Your usage is {percent_above_benchmark:.2f}% compared to Best Practice Target.")

        bench_co2 = bench_entry.get("co2")
        co2_percent = ((estimated_co2_kg - bench_co2) / bench_co2) * 100 if bench_co2 else None

    # Determine industry class and price modifier
    industry_class = facility_data.get("industry_class", "household")
    industry_modifier = config["industry_classes"].get(industry_class, 1.0)
    print(f"[DEBUG] Industry class: {industry_class}")
    print(f"[DEBUG] Industry modifier: {industry_modifier}")

    # Get power grid region
    power_region = config["power_grid_regions"].get(input_data.region)
    if not power_region:
        raise HTTPException(status_code=400, detail=f"Region '{input_data.region}' has no power grid mapping.")

    # If facility type is data_center → apply power region multiplier
    if input_data.facility_type == "data_center":
        power_multiplier = facility_data.get("power_region_multipliers", {}).get(power_region, 1.0)
        estimated_kwh *= power_multiplier
        print(f"[DEBUG] Applying power region multiplier for data_center: {power_multiplier}")
        print(f"[DEBUG] Estimated kWh after region multiplier: {estimated_kwh}")

    # Determine price per kWh
    if input_data.custom_price_per_kwh is not None:
        effective_price = input_data.custom_price_per_kwh
        price_source = "custom"
        print(f"[DEBUG] Using custom price per kWh: {effective_price}")
    else:
        try:
            base_price = asyncio.run(fetch_average_price(power_region))
            effective_price = base_price * industry_modifier
            price_source = "api"
            print(f"[DEBUG] Base price from API (NOx): {base_price}")
        except Exception:
            base_price = config["pricing"].get("default_nok_per_kwh", 1.20)
            effective_price = base_price * industry_modifier
            price_source = "default"
            print(f"[DEBUG] Fallback base price: {base_price}")

        print(f"[DEBUG] Effective price after modifier: {effective_price} (source: {price_source})")

    estimated_cost_nok = estimated_kwh * effective_price
    print(f"[DEBUG] Total estimated cost (kWh × price): {estimated_cost_nok}")
    print("------------------------------------------------------------")

    # Calculate Best Practice Target cost
    bench_cost = bench_kwh * effective_price if bench_kwh else None
    cost_percent = ((estimated_cost_nok - bench_cost) / bench_cost) * 100 if bench_cost else None

    return {
        "status": "valid",
        "estimated_kwh": round(estimated_kwh, 2),
        "estimated_co2_kg": round(estimated_co2_kg, 2),
        "estimated_cost_nok": round(estimated_cost_nok, 2),
        "metadata": {
            "region": input_data.region,
            "power_grid_region": power_region,
            "industry_class": industry_class,
            "industry_modifier": industry_modifier,
            "price_per_kwh": round(effective_price, 3),
            "price_source": price_source,
            "emission_factor_used": emission_factor,
            "emission_factor_timestamp": emission_timestamp,

            **({"estimated_baseline_kwh": baseline} if baseline is not None else {}),
            **({"size_multiplier": multiplier} if multiplier is not None else {}),
            "best_practice_target": {
                "target_kwh": bench_kwh,
                "percent_above_target_kwh": round(percent_above_benchmark, 2) if percent_above_benchmark is not None else None,
                "target_co2": bench_co2,
                "percent_above_target_co2": round(co2_percent, 2) if co2_percent is not None else None,
                "target_cost": bench_cost,
                "percent_above_target_cost": round(cost_percent, 2) if cost_percent is not None else None
            }
        },
        "received": input_data.model_dump()
    }

@router.get("/regions")
def get_regions():
    config = load_static_config()
    return {"regions": config["regions"]}

@router.get("/facility-types")
def get_facility_types():
    config = load_static_config()
    return {"facility_types": list(config["facility_types"].keys())}
