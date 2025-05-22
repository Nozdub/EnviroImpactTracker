from pydantic import BaseModel
from typing import Optional, Literal


class CalculationInput(BaseModel):
    region: Literal[
        "Østfold", "Akershus", "Oslo", "Hedmark", "Oppland", "Buskerud", "Vestfold",
        "Telemark", "Agder", "Rogaland", "Hordaland", "Møre og Romsdal",
        "Sogn og Fjordane", "Trøndelag", "Nordland", "Troms", "Finnmark"
    ]
    facility_type: Literal[
        "data_center", "factory", "hospital", "farm", "warehouse", "office_building",
        "school", "supermarket", "retail_store", "university", "municipal_building"
    ]
    size: Literal["small", "medium", "large"]

    custom_kwh: Optional[float] = None
    usage_pattern: Optional[str] = None
    custom_emission_factor: Optional[float] = None
    custom_price_per_kwh: Optional[float] = None
