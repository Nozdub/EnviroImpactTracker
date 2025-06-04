from fastapi.testclient import TestClient
from app.main import app
import pytest
from unittest.mock import patch

client = TestClient(app)


@pytest.mark.parametrize("payload", [
    {
        "region": "Oslo",
        "facility_type": "data_center",
        "size": "medium"
    },
    {
        "region": "Trøndelag",
        "facility_type": "school",
        "size": "large"
    },
    {
        "region": "Nordland",
        "facility_type": "farm",
        "size": "small",
        "custom_kwh": 100000,
        "custom_emission_factor": 0.015,
        "custom_price_per_kwh": 1.10
    }
])
def test_calculate_valid_request(payload):
    response = client.post("/calculate", json=payload)
    assert response.status_code == 200

    data = response.json()

    # Basic checks
    assert data["status"] == "valid"
    assert "estimated_kwh" in data
    assert "estimated_cost_nok" in data
    assert "estimated_co2_kg" in data

    # Check metadata presence
    assert "metadata" in data
    assert "region" in data["metadata"]
    assert "power_grid_region" in data["metadata"]


def test_get_regions():
    response = client.get("/regions")
    assert response.status_code == 200
    json_data = response.json()
    assert "regions" in json_data
    assert isinstance(json_data["regions"], list)
    assert len(json_data["regions"]) > 0


def test_get_facility_types():
    response = client.get("/facility-types")
    assert response.status_code == 200
    json_data = response.json()
    assert "facility_types" in json_data
    assert isinstance(json_data["facility_types"], list)
    assert len(json_data["facility_types"]) > 0


def test_calculate_custom_kwh_overrides_baseline():
    payload = {
        "region": "Oslo",
        "facility_type": "hospital",
        "size": "small",
        "custom_kwh": 123456.78
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert abs(data["estimated_kwh"] - 123456.78) < 0.01  # Should match custom input


def test_calculate_custom_price_used():
    payload = {
        "region": "Oslo",
        "facility_type": "office_building",
        "size": "medium",
        "custom_price_per_kwh": 2.22
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["price_per_kwh"] == 2.22
    assert data["metadata"]["price_source"] == "custom"


def test_calculate_custom_emission_factor_used():
    payload = {
        "region": "Oslo",
        "facility_type": "school",
        "size": "large",
        "custom_emission_factor": 0.012
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["metadata"]["emission_factor_used"] == 0.012


def test_data_center_power_region_multiplier_applied():
    payload = {
        "region": "Oslo",  # NO1 → 1.25
        "facility_type": "data_center",
        "size": "medium"
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()

    # Correct values from current static_config.json
    baseline = 6451520
    size_multiplier = 1.0
    power_region_multiplier = 1.25

    expected_kwh = baseline * size_multiplier * power_region_multiplier
    assert abs(data["estimated_kwh"] - expected_kwh) < 1.0


def test_calculate_emission_api_fallback():
    with patch("app.api.calculate.fetch_emission_factor", side_effect=Exception("API down")):
        payload = {
            "region": "Oslo",
            "facility_type": "school",
            "size": "medium"
        }

        response = client.post("/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Sets the fallback config
        assert data["metadata"]["emission_factor_used"] == 0.017


def test_calculate_price_api_fallback():
    with patch("app.api.calculate.fetch_average_price", side_effect=Exception("API down")):
        payload = {
            "region": "Oslo",
            "facility_type": "school",
            "size": "medium"
        }

        response = client.post("/calculate", json=payload)
        assert response.status_code == 200
        data = response.json()
        # Fallback to set modifiers for pricing, industry type and location
        expected_price = 1.20 * 0.85
        assert abs(data["metadata"]["price_per_kwh"] - expected_price) < 0.01
        assert data["metadata"]["price_source"] == "default"


# NEGATIVE TESTS
def test_calculate_invalid_region():
    payload = {
        "region": "Atlantis", # Obvious incorrect region right, no atlantis here right?
        "facility_type": "data_center",
        "size": "medium"
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "region"]


def test_calculate_invalid_facility_type():
    payload = {
        "region": "Oslo",
        "facility_type": "superhero factory", # Only in Marvel or DC
        "size": "large"
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "facility_type"]


def test_calculate_invalid_size():
    payload = {
        "region": "Nordland",
        "facility_type": "school",
        "size": "Gigantic"
    }

    response = client.post("/calculate", json=payload)
    assert response.status_code == 422
    data = response.json()
    assert data["detail"][0]["loc"] == ["body", "size"]



