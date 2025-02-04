import requests
from dotenv import load_dotenv
import os
from twilio.rest import Client

load_dotenv()

api_key = os.getenv("API_KEY") 
#twilio stuff
twilio_key = os.getenv("TWILIO_API_KEY")
account_sid = os.getenv("ACCOUNT_SID")




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
    client = Client(account_sid, twilio_key)
    message = client.messages.create(
    body="its gonna rain today",
    #twilio phone number
    from_="+18557188705",
    #mine phone number
    to="+18179752705",
    )
    print(message.status)
