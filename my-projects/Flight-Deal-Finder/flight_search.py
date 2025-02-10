import requests
import os
from dotenv import load_dotenv

load_dotenv()

FLIGHT_API_KEY = os.getenv("FLIGHT_API_KEY")
FLIGHT_SECRET_KEY = os.getenv("FLIGHT_SECRET_KEY")
class FlightSearch:

    #This class is responsible for talking to the Flight Search API.
    pass