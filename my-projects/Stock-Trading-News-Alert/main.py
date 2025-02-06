import requests
import os
from dotenv import load_dotenv
from twilio.rest import Client

#importing api keys / stock names

load_dotenv()

alpha_API = os.getenv("API_KEY")
news_API = os.getenv("NEWS_API_KEY")
twilio_API = os.getenv("TWILIO_API_KEY")
account_SID = os.getenv("ACCOUNT_SID")


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"

need_news = False

#params and requesting from alphavantage API

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

#get two most recent dates and their values

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

#find the difference between each key and see
#if that difference is greater than 5%
greatestChange = 0
maxChange = 0
for key, label in fields.items():
    (latest_val) = float(latestvalue[key])
    (prev_val) =  float(previousvalue[key])
    

    percent_change = ((latest_val - prev_val) / prev_val) * 100
    
    if abs(percent_change) >= 5:
        
        greatestChange = max(greatestChange, percent_change)
        if abs(maxChange) < greatestChange:
            maxChange = percent_change
        
        need_news = True

#get news from that stock (this case TSLA) using news API if any stock > 5% change
if need_news:
    url = "https://newsapi.org/v2/everything"
    params = {
        "apiKey": news_API,
        "q": "Tesla OR TSLA",
        "sortBy": "publishedAt",
        "language": "en",
    }
    r = requests.get(url, params)
    r.raise_for_status()

    data = r.json()

    #get 3 most recent sources
    data = data['articles']
    sorted_articles = sorted(data, key = lambda x: x['publishedAt'], reverse= True)
    recent_sources = [article for article in sorted_articles[:3]]

    if maxChange < 0:
        for article in recent_sources:
            client = Client(account_SID, twilio_API)
            message = client.messages.create(
            body=f"TSLA: 🔻{greatestChange}%\n{recent_sources["author"]}:{recent_sources["title"]}\n{recent_sources["description"]}\n{recent_sources["url"]}",
            #twilio phone number
            from_="+18557188705",
            #mine phone number
            to="+18179752705",
            )
            print(message.status)
    else:
        for article in recent_sources:
            client = Client(account_SID, twilio_API)
            message = client.messages.create(
            body=f"TSLA: 🔺{greatestChange}%\n{recent_sources["author"]}:{recent_sources["title"]}\n{recent_sources["description"]}\n{recent_sources["url"]}",
            #twilio phone number
            from_="+18557188705",
            #mine phone number
            to="+18179752705",
            )
            print(message.status)