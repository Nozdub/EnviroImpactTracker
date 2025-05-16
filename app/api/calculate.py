from fastapi import APIRouter, HTTPException
from app.models.calculation_input import CalculationInput
from app.services.config_loader import load_static_config

router = APIRouter()


@router.post("/calculate")
def calculate(input_data: CalculationInput):
    config = load_static_config()
    print(" Loaded config")

    # Validate location
    valid_locations = config.get("valid_locations", [])
    if input_data.location not in valid_locations:
        print(f" Invalid location: {input_data.location}")
        raise HTTPException(status_code=400, detail=f"Invalid location: {input_data.location}")

    # Validate facility type
    facility_config = config.get("facility_types", {})
    if input_data.facility_type not in facility_config:
        print(f" Invalid facility type: {input_data.facility_type}")
        raise HTTPException(status_code=400, detail=f"Invalid facility type: {input_data.facility_type}")

    # Validate size
    size_multipliers = facility_config[input_data.facility_type].get("size_multipliers", {})
    if input_data.size not in size_multipliers:
        print(f" Invalid size: {input_data.size}")
        raise HTTPException(status_code=400, detail=f"Invalid size '{input_data.size}' for facility type '{input_data.facility_type}'")

    print(" All inputs valid")

    # Calculate expected electricity usage
    try:
        facility_data = config["facility_types"][input_data.facility_type]
        multiplier = facility_data["size_multipliers"][input_data.size]
        print(f" Multiplier: {multiplier}")

        if input_data.custom_kwh is not None:
            print(f"Custom KWh provided: {input_data.custom_kwh}")
            estimated_kwh = float(input_data.custom_kwh) * multiplier
        else:
            facility_data = config["facility_types"][input_data.facility_type]
            baseline = facility_data["baseline_kwh"]
            multiplier = facility_data["size_multipliers"][input_data.size]
            estimated_kwh = baseline * multiplier

            print(f"Using baseline: {baseline}")
            print(f"Using size multiplier: {multiplier}")
            print(f"Estimated kWh (baseline × multiplier): {estimated_kwh}")

    except Exception as e:
        print(" ERROR during kWh calculation:", e)
        raise HTTPException(status_code=500, detail="Internal server error during energy calculation")

    # Emission factor from config
    emission_factor = (
        input_data.custom_emission_factor
        if input_data.custom_emission_factor is not None
        else config["emission_factors"]["default"]
    )
    estimated_co2_kg = estimated_kwh * emission_factor

    # Load pricing info
    price_per_kwh = (
        input_data.custom_price_per_kwh
        if input_data.custom_price_per_kwh is not None
        else config["pricing"]["default_nok_per_kwh"]
    )
    estimated_cost_nok = estimated_kwh * price_per_kwh

    print(f"Emission factor used: {emission_factor}")
    print(f"Price per kWh used: {price_per_kwh}")
    print(f"Estimated c02 output: {estimated_co2_kg}")
    print(f"Estimated cost in nok: {estimated_cost_nok}")

    # Return result
    return {
        "status": "valid",
        "estimated_kwh": estimated_kwh,
        "estimated_co2_kg": round(estimated_co2_kg, 2),
        "estimated_cost_nok": round(estimated_cost_nok, 2),
        "received": input_data.model_dump()
    }


