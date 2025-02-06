import requests
import os
from dotenv import load_dotenv

#importing api keys / stock names

load_dotenv()

alpha_API = os.getenv("API_KEY")
news_API = os.getenv("NEWS_API_KEY")

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
for key, label in fields.items():
    (latest_val) = float(latestvalue[key])
    (prev_val) =  float(previousvalue[key])
    

    percent_change = ((latest_val - prev_val) / prev_val) * 100
    
    if abs(percent_change) >= 5:
        greatestChange = max(greatestChange, percent_change)
        need_news = True

#get news from that stock (this case TSLA) using news API
if True:
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
    recent_sources = [article['source']['name'] for article in sorted_articles[:3]]
    print(recent_sources)


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

