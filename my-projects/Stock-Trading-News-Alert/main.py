import requests
import os
from dotenv import load_dotenv

load_dotenv()
alpha_API = os.getenv("API_KEY")
STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

parameters = {
    "apikey": alpha_API,
    "function":  "TIME_SERIES_DAILY",
    "symbol": STOCK ,
}

url = f'https://www.alphavantage.co/query'
r = requests.get(url, params= parameters)
r.raise_for_status()
data = r.json() 
data = data['Time Series (Daily)']

sorted_dates = sorted(data.keys(), reverse = True)
latestday, previousday = sorted_dates[:2]

latestvalue = data[latestday]
previousvalue = data[previousday]

fields = {
    "1. open": "Open Price",
    "2. high": "High Price",
    "3. low": "Low Price",
    "4. close": "Close Price",
    "5. volume": "Volume"
}

for key, label in fields.items():
    latest_val = (latestvalue[key])
    prev_val = (previousvalue[key])
    

    percent_change = ((latest_val - prev_val) / prev_val) * 100
    
    if abs(percent_change) >= 5:
        print("Get News")

## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

## STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 

## STEP 3: Use https://www.twilio.com
# Send a seperate message with the percentage change and each article's title and description to your phone number. 


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

