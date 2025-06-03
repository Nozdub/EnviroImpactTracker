from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

def test_calculate_valid_request():
    response = client.post("/calculate", json={
        "region": "Oslo",
        "facility_type": "office_building",
        "size": "medium"
    })
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