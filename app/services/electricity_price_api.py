import httpx
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

load_dotenv()
STROMPRISER_API_KEY = os.getenv("STROMPRISER_API_KEY")

POWER_REGION_MAP = {
    "NO1": 1,
    "NO2": 2,
    "NO3": 3,
    "NO4": 4,
    "NO5": 5,
}

async def fetch_average_price_last_12_months(power_region: str) -> float:
    region_id = POWER_REGION_MAP.get(power_region)
    if not region_id:
        raise ValueError(f"Unknown power region: {power_region}")

    end_date = datetime.now().date()
    start_date = end_date - timedelta(days=365)

    url = (
        f"https://api.strompriser.no/public/prices"
        f"?country=Norway&startDate={start_date}&endDate={end_date}&region={region_id}"
    )

    headers = {
        "api-key": STROMPRISER_API_KEY
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            if not data or not isinstance(data, list) or "dailyPriceArray" not in data[0]:
                raise ValueError("Unexpected API response format")

            price_list = data[0]["dailyPriceArray"]
            average_ore = sum(price_list) / len(price_list)
            average_nok = round(average_ore / 100, 4)
            return average_nok

    except Exception as e:
        print(f"[ERROR] Failed to fetch 12-month average price for {power_region}: {e}")
        raise
