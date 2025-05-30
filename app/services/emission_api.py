import httpx
from dotenv import load_dotenv
import os

load_dotenv()

API_KEY = os.getenv("ELECTRICITYMAP_API_KEY")


COUNTRY_CODE = "NO"


async def fetch_emission_factor(country_code: str = COUNTRY_CODE) -> float:

    url = "https://api.electricitymap.org/v3/carbon-intensity/latest"
    headers = {
        "auth-token": API_KEY
    }
    params = {
        "countryCode": country_code
    }

    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.get(url, headers=headers, params=params)
            response.raise_for_status()

            data = response.json()
            g_per_kwh = data["carbonIntensity"]
            timestamp = data["datetime"]
            print(f"[DEBUG] Fetched emission factor: {g_per_kwh} gCo2eq/kWh")

            # Convert to kg co2 per kWh
            kg_per_kwh = g_per_kwh / 1000.0
            return round(kg_per_kwh, 4), timestamp

    except Exception as e:
        print(f"[ERROR] Failed to fetch emission factor: {e}")
        raise


if __name__ == "__main__":
    import asyncio

    factor = asyncio.run(fetch_emission_factor())
    print(f"Current emission factor (kg CO2/kWh): {factor}")

