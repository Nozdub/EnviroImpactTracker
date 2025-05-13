from fastapi import APIRouter
from app.models.calculation_input import CalculationInput

print("🚨 CALCULATE ROUTE FILE LOADED 🚨")

router = APIRouter()


@router.post("/calculate")
def calculate(input_data: CalculationInput):
    print("🧠 calculate() function triggered")
    return {
        "status": "ok",
        "received": input_data.model_dump()
    }
