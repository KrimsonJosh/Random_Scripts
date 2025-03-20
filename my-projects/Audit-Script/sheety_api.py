# sheety_api.py
import requests

def post_to_sheety(sheety_url, sheety_token, row_data):
    headers = {"Content-Type": "application/json"}
    if sheety_token:
        headers["Authorization"] = f"Bearer {sheety_token}"  # if your Sheety is private

    body = {
        "sheet1": row_data  # or whichever tab name Sheety expects
    }
    resp = requests.post(sheety_url, headers=headers, json=body)
    return resp
