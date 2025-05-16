from fastapi import APIRouter, HTTPException
from app.models.calculation_input import CalculationInput
from app.services.config_loader import load_static_config

router = APIRouter()


@router.post("/calculate")
def calculate(input_data: CalculationInput):
    config = load_static_config()

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

    # Base calculations

    # Determine baseline kWh
    if input_data.custom_kwh is not None:
        estimated_kwh = float(input_data.custom_kwh)
    else:
        baseline = facility_data["baseline_kwh"]
        multiplier = facility_data["size_multipliers"][input_data.size]
        estimated_kwh = baseline * multiplier

        # Emission calculation
        emission_factor = input_data.custom_emission_factor or config["emission_factors"]["default"]
        estimated_co2_kg = estimated_kwh * emission_factor

        # Determine industry class and price modifier
        industry_class = facility_data.get("industry_class", "household")
        industry_modifier = config["industry_classes"].get(industry_class, 1.0)

        # Get power grid region and base price
        power_region = config["power_grid_regions"].get(input_data.region)
        if not power_region:
            raise HTTPException(status_code=400, detail=f"Region '{input_data.region}' has no power grid mapping.")

        # Placeholder: Fetch dynamic price here in future implementation
        base_price = config["pricing"].get("default_nok_per_kwh", 1.20)

        # Override with user input if given
        effective_price = input_data.custom_price_per_kwh or (base_price * industry_modifier)
        estimated_cost_nok = estimated_kwh * effective_price

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
                "emission_factor_used": emission_factor
            },
            "received": input_data.model_dump()
        }


@router.get("/regions")
def get_regions():
    config = load_static_config()
    return {"regions": config["regions"]}