import requests
import os
from dotenv import load_dotenv 
from datetime import datetime
load_dotenv()

API_KEY = os.getenv("API_KEY")
APP_ID = os.getenv("APP_ID")

sheety_URL = "https://api.sheety.co/14cd46bb3822233f46328aed0d240016/workoutTracker/workouts"

GENDER = "male"
WEIGHT_KG = 100
HEIGHT_CM = 60
AGE = 18




headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,
    "Content-Type": "application/json"
}

exercise_endpoint = "https://trackapi.nutritionix.com/v2/natural/exercise"

exercise_text = input("Tell me which exercises you did: ")

headers = {
    "x-app-id": APP_ID,
    "x-app-key": API_KEY,
}

parameters = {
    "query": exercise_text,
    "gender": GENDER,
    "weight_kg": WEIGHT_KG,
    "height_cm": HEIGHT_CM,
    "age": AGE
}

response = requests.post(exercise_endpoint, json=parameters, headers=headers)
response = response.json()

today_date = datetime.now().strftime("%d/%m/%Y")
now_time = datetime.now().strftime("%X")

for exercise in response["exercises"]:
    sheet_inputs = {
        "workout": {
            "date": today_date,
            "time": now_time,
            "exercise": exercise["name"].title(),
            "duration": exercise["duration_min"],
            "calories": exercise["nf_calories"]
        }
    }

sheet_response = requests.post(sheety_URL, json=sheet_inputs)
print(sheet_response.text)
