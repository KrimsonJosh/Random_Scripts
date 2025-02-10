import requests
import os
from dotenv import load_dotenv

load_dotenv()

FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY")
FLIGHT_SECRET_KEY = os.getenv("FLIGHT_SECRET_KEY")
ORIGIN_LOCATION = "DFW"

url = "https://test.api.amadeus.com/v2/shopping/flight-offers"


def get_access_token():
    token_url = "https://test.api.amadeus.com/v1/security/oauth2/token"
    headers = {"Content-Type": "application/x-www-form-urlencoded"}
    data = {
        "grant_type": "client_credentials",
        "client_id": FLIGHT_API_KEY,
        "client_secret": FLIGHT_SECRET_KEY
    }
    response = requests.post(token_url, headers=headers, data=data)
    response.raise_for_status()  
    return response.json()["access_token"]

def get_flight_destinations(origin, max_price, token):
    url = f"https://test.api.amadeus.com/v1/shopping/flight-destinations?origin={origin}&maxPrice={max_price}"
    headers = {"Authorization": f"Bearer {token}"}

    response = requests.get(url, headers=headers)
    response.raise_for_status()
    return response.json()


class FlightSearch:

    #This class is responsible for talking to the Flight Search API.
    pass