from pydantic import BaseModel
from typing import Optional


class CalculationInput(BaseModel):
    location: str
    facility_type: str
    size: str
    custom_kwh: Optional[float] = None
    machine_count: Optional[int] = None
    usage_pattern: Optional[str] = None
