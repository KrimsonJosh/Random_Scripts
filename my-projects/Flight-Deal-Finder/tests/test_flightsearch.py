import pytest
from flight_search import get_access_token, get_flight_destinations


def test_get_access_token():
    token = get_access_token()
    assert token is not None, "Failed to get access token"
    assert len(token) > 0, "Access token is empty"
    print(f"Access token: {token}")

def test_get_flight_destinations():
    token = get_access_token()
    response = get_flight_destinations("DFW", 200, token)
    assert "data" in response, "No data found in response"
    assert len(response["data"]) > 0, "No destinations returned"
    print(f"First destination: {response['data'][0]['destination']}")