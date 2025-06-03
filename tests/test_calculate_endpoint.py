from fastapi.testclient import TestClient
from app.main import app
import pytest

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



