import requests
from twilio.rest import Client
import pandas as pd
import datetime

today = (datetime.datetime.now().date())
yesterday = (today - datetime.timedelta(days=1))
day_before = yesterday - datetime.timedelta(days=1)
STOCK = "TSLA"
COMPANY_NAME = "Tesla"

# STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
stocks_api = 'SOMJGA03XRBHJPW7'
parameters = {
    'function': 'TIME_SERIES_DAILY',
    'symbol': STOCK,
    'apikey': stocks_api
}
url = 'https://www.alphavantage.co/query'
stock_response = requests.get(url=url, params=parameters)
stocks_data = stock_response.json()
print(stocks_data)
stocks_df = pd.DataFrame(stocks_data)
stocks_df.to_csv(path_or_buf='stocks df', sep=',')

yesterday_close = float(stocks_data['Time Series (Daily)'][yesterday.strftime("%Y-%m-%d")]['4. close'])
day_before_close = float(stocks_data['Time Series (Daily)'][day_before.strftime("%Y-%m-%d")]['4. close'])


def percentage_change(old, new):
    if old == 0:
        return float('inf')  # Prevent division by zero
    return ((new - old) / old) * 100


change = percentage_change(yesterday_close, day_before_close)

# STEP 2: Use https://newsapi.org
# Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME. 
stock_news_api = 'API'
news_url = 'https://newsapi.org/v2/everything?'

news_params = {
    'qInTitle': COMPANY_NAME,
    'from': yesterday.strftime("%Y-%m-%d"),
    'sortBy': 'popularity',
    'apiKey': stock_news_api,
    'language': 'en'
}

news_response = requests.get(url=news_url, params=news_params)
news_data = news_response.json()
print(news_data)


def pos_neg_change(dif, title, description):
    message_body = ''
    if dif > 0:
        message_body = f"""
                TSLA: 🔺{abs(dif)} %\n
                Headline: {title}\n 
                Brief: {description}
            """
    elif dif < 0:
        message_body = f"""
                        TSLA: 🔻{abs(dif)}%\n
                        Headline: {title}\n 
                        Brief: {description}
                    """
    else:
        message_body = f"""
                                TSLA: =={abs(dif)}%\n
                                Headline: {title}\n 
                                Brief: {description}
                            """
    return message_body


for news in news_data['articles'][0:3]:
    headline = news['title']
    brief = news['description']
    body = pos_neg_change(change, headline, brief)
    print(body)

    # STEP 3: Use https://www.twilio.com
    # Send a separate message with the percentage change and each article's title and description to your phone number.
    account_sid = 'ATWILLIO SID'
    auth_token = 'SECRET TOKEN'
    client = Client(account_sid, auth_token)
    message = client.messages.create(
        from_='TWILLIO NUMBER',
        body=body,
        to='RECEIVER'
    )

    print(message.sid)
