from fastapi import APIRouter, HTTPException
from app.models.calculation_input import CalculationInput
from app.services.config_loader import load_static_config
import asyncio
from app.services.electricity_price_api import fetch_average_price
from app.services.benchmark_loader import load_benchmark_data

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


    # Emission calculation
    emission_factor = input_data.custom_emission_factor or config["emission_factors"]["default"]
    estimated_co2_kg = estimated_kwh * emission_factor
    print(f"[DEBUG] Emission factor used: {emission_factor}")
    print(f"[DEBUG] Estimated CO₂ (kWh × factor): {estimated_co2_kg}")

    # Benchmark comparison
    bench_kwh = None
    percent_above_benchmark = None

    bench_entry = benchmark.get(input_data.facility_type, {}).get(input_data.size)
    if bench_entry:
        bench_kwh = bench_entry.get("kwh")
        if bench_kwh:
            percent_above_benchmark = ((estimated_kwh - bench_kwh) / bench_kwh) * 100
            print(f"[DEBUG] Benchmark kWh: {bench_kwh}")
            print(f"[DEBUG] Your usuage is {percent_above_benchmark:.2f}% compared to benchmark.")
    else:
        print(f"[DEBUG] No benchmark data available for {input_data.facility_type} ({input_data.size})")




    # Determine industry class and price modifier
    industry_class = facility_data.get("industry_class", "household")
    industry_modifier = config["industry_classes"].get(industry_class, 1.0)
    print(f"[DEBUG] Industry class: {industry_class}")
    print(f"[DEBUG] Industry modifier: {industry_modifier}")

    # Get power grid region
    power_region = config["power_grid_regions"].get(input_data.region)
    if not power_region:
        raise HTTPException(status_code=400, detail=f"Region '{input_data.region}' has no power grid mapping.")

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

    bench_co2 = bench_entry.get("co2") if bench_entry else None
    co2_percent = ((estimated_co2_kg - bench_co2) / bench_co2) * 100 if bench_co2 else None

    bench_cost = bench_entry.get("cost") if bench_entry else None
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
            **({"estimated_baseline_kwh": baseline} if baseline is not None else {}),
            **({"size_multiplier": multiplier} if multiplier is not None else {}),
            "benchmark": {
                "benchmark_kwh": bench_kwh,
                "percent_above_benchmark": round(percent_above_benchmark, 2) if percent_above_benchmark is not None else None,
                "benchmark_co2": bench_co2,
                "percent_above_co2": round(co2_percent, 2) if co2_percent is not None else None,
                "benchmark_cost": bench_cost,
                "percent_above_cost": round(cost_percent, 2) if cost_percent is not None else None
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
