import requests
import datetime

LAT = 49.609779
LONG = -112.690918

parameters = {
    "lat": LAT,
    "lng": LONG,
    "formatted": 0
}

response = requests.get("https://api.sunrise-sunset.org/json", params = parameters)



response.raise_for_status()
data = response.json()

splitdata = data.split("T")
splitdata = splitdata[1](":")

sunrise = data["results"]["sunrise"]
sunset = data["results"]["sunset"]



currTime = datetime.now()
hour = currTime.hour

print(f"Your sunrise will be {sunrise}, and your sunset will be {sunset}.\n")


