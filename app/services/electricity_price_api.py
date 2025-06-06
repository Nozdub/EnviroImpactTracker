# app/services/electricity_price_api.py

import httpx
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv

# Load API Key
load_dotenv()
STROMPRISER_API_KEY = os.getenv("STROMPRISER_API_KEY")

# Map NOx to Strompriser.no region IDs
STROMPRISER_REGION_MAP = {
    "NO1": 1,
    "NO2": 2,
    "NO3": 3,
    "NO4": 4,
    "NO5": 5
}

async def fetch_average_price_last_12_months(power_region: str) -> float:
    """Fetches 12-month average kwh price for selected power grid region (from strompriser.no)"""

    region_id = STROMPRISER_REGION_MAP.get(power_region)

    if region_id is None:
        raise ValueError(f"Invalid power region: {power_region}")

    today = datetime.utcnow().date()
    one_year_ago = today - timedelta(days=365)

    url = (
        f"https://api.strompriser.no/public/prices"
        f"?country=Norway"
        f"&startDate={one_year_ago}"
        f"&endDate={today}"
        f"&region={region_id}"
    )

    headers = {
        "Authorization": f"Bearer {STROMPRISER_API_KEY}"
    }

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()

            # Expecting: data = list of { "price": value, ... }
            prices = [entry["price"] for entry in data]

            if not prices:
                raise ValueError("No price data returned from strompriser.no API.")

            avg_price_nok = sum(prices) / len(prices)

            return round(avg_price_nok, 4)

    except Exception as e:
        print(f"[ERROR] Failed to fetch 12-month average price for {power_region}: {e}")
        raise
