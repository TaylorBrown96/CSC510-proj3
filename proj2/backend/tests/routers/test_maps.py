import pytest
import asyncio
from httpx import AsyncClient

from src.eatsential.models.models import Restaurant


def make_mock_response(results):
    class MockResponse:
        def __init__(self, results):
            self._results = {"results": results}
            self.status_code = 200

        def json(self):
            return self._results

        def raise_for_status(self):
            return None

    return MockResponse(results)


@pytest.mark.asyncio
async def test_maps_search_saves_restaurants(monkeypatch, client, db):
    # Prepare a fake Google Places result
    fake_place = {
        "place_id": "ChIJFAKEPLACEID1234567890",
        "name": "Test Sushi Spot",
        "formatted_address": "123 Test St, Testville",
        "types": ["restaurant", "japanese"],
        "geometry": {"location": {"lat": 35.0, "lng": -78.0}},
    }

    async def fake_get(self, url, params=None):
        return make_mock_response([fake_place])

    monkeypatch.setattr("httpx.AsyncClient.get", fake_get)

    # Call the maps endpoint with a cuisine param
    res = client.get("/api/maps/search?query=Test%20Sushi&cuisine=japanese")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)
    assert len(data) == 1
    assert data[0]["place_id"] == fake_place["place_id"]

    # Verify restaurant saved in DB
    saved = db.query(Restaurant).filter(Restaurant.id == fake_place["place_id"]).first()
    assert saved is not None
    assert saved.name == fake_place["name"]
    assert saved.cuisine == "japanese"
