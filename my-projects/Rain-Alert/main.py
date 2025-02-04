import requests
from dotenv import load_dotenv
import os

load_dotenv()
api_key = os.getenv("API_KEY")

lati = 32.948334
long = -96.729851


url = "https://api.openweathermap.org/data/2.5/forecast"

weather_params = {
    "lon": long,
    "lat": lati,
    "appid": api_key,
    "cnt": 4
}

response = requests.get(url, params = weather_params)

response.raise_for_status()

weather_data = response.json()
mylist = weather_data["list"]
will_rain = False
#hour data from weather api
for hour_data in weather_data["list"]:
    cond_code= hour_data["weather"][0]["id"]
    #there is rain
    if int(cond_code) < 700:
        will_rain = True
    #everything ok
#if there is rain between 6-6pm
if will_rain:
    print("Bring umbrella")
