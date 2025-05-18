import httpx
from datetime import datetime


async def fetch_average_price(power_region: str) -> float:
    """Fetches accurate kwh price for selected power grid region"""

    today = datetime.now()
    year = today.strftime("%Y")
    month_day = today.strftime("%m-%d")
    url = f"https://www.hvakosterstrommen.no/api/v1/prices/{year}/{month_day}_{power_region}.json"

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url)
            response.raise_for_status()
            prices = response.json()
            avg_price_øre = sum(entry["NOK_per_kWh"] for entry in prices) / len(prices)
            return round(avg_price_øre, 4)
    except Exception as e:
        print(f"[ERROR] Failed to fetch price for {power_region}: {e}")
        raise