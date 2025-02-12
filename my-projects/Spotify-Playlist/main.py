import requests
from datetime import datetime
from bs4 import BeautifulSoup

# Try Catch for inputting correct TimeStamp

while True:
    try:
        TravelYear = input("What year would you like to travel to? Enter in format YYYY-MM-DD:")

        valid_date = datetime.strptime(TravelYear, "%Y-%m-%d")
        break
    except ValueError:
        print("invalid format, please try again in YYYY-MM-DD format.")

# Make a request to billboard.com

url = "https://www.billboard.com/"
header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
response = requests.get(url, header)
response.raise_for_status()


# Turn that shit into soup 

response = response.text 
soup = BeautifulSoup(response, "html.parser")


