import requests
import os 
from dotenv import load_dotenv

load_dotenv()

mytoken = os.getenv("API_KEY")

pixela_url = "https://pixe.la/v1/users"

pixela_params = {
    "token": mytoken,
    "username": "JoshuaMoinzadeh",
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}
response = requests.post(url = pixela_url, json=pixela_params)
