import requests
import os 
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

USERNAME = "joshuamoinzadeh"
mytoken = os.getenv("API_KEY")

pixela_url = "https://pixe.la/v1/users"

pixela_params = {
    "token": mytoken,
    "username": USERNAME,
    "agreeTermsOfService": "yes",
    "notMinor": "yes",
}

#post config
graph_endpoint = f"{pixela_url}/{USERNAME}/graphs"

graph_config = {
    "id": "apples",
    "name": "github",
    "unit": "contribution",
    "type": "int",
    "color": "shibafu"
}
response = requests.post(url = pixela_url, json = pixela_params)

header = {
    "X-USER-TOKEN": mytoken
}

response = requests.post(url = graph_endpoint, json = graph_config, headers = header)

today = datetime.now()
todayDate = today.strftime("%Y%m%d")
pixel_config = {
    "date": todayDate,
    "quantity": "13",
}

pixela_creation_endpoint = f"{pixela_url}/{USERNAME}/graphs/apples"
response = requests.post(url = pixela_creation_endpoint, json = pixel_config, headers = header)

print(response.text)

#put config 
put_creation_endpoint = f"{pixela_url}/{USERNAME}/graphs/apples/{todayDate}"

put_config = {
    "quantity": "12",
}

requests.put(put_creation_endpoint, json = put_config, headers = header)

delete_creation_endpoint = f"{pixela_url}/{USERNAME}/graphs/apples/{todayDate}"

requests.delete(delete_creation_endpoint, headers = header)

