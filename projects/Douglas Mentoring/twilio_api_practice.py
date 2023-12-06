from twilio.rest import Client
import requests, os
from datetime import datetime, timedelta


def get_stock_data():
    # Pull data from API

    global STOCK
    STOCK = "TSLA"
    alphavantage_api_key = os.environ["stock_key"]

    parameters = {
        "function": "TIME_SERIES_DAILY",
        "symbol": STOCK,
        "apikey": alphavantage_api_key
    }
    response = requests.get("https://www.alphavantage.co/query", params=parameters)
    return response.json()


def get_stock_values(stock_data, yesterday, day_b_yesterday):
    # Get the value from CLOSED
    # check if its 5% lower or higher
    # if no variance of 5% no more actions required

    yesterday_close = float(stock_data["Time Series (Daily)"][f'{yesterday}']["4. close"])
    day_b_yesterday_close = float(stock_data["Time Series (Daily)"][f'{day_b_yesterday}']["4. close"])
    print(f"##{yesterday_close}")
    print(f"##{day_b_yesterday_close}")

    five_percent_less = float(day_b_yesterday_close) * 0.95
    five_percent_higher = float(day_b_yesterday_close) * 1.05
    print(f"**{five_percent_less}")
    print(f"**{five_percent_higher}")

    if yesterday_close >= five_percent_less or yesterday_close <= five_percent_higher:
        print('Get news')
        return True
    else:
        print('Not today!')
        return False


def calculate_dates():
    # Here we'll check the dates
    # Expect to get update only from last 2 days
    # If Monday or Sunday no updates required
    week_day = datetime.now().date().weekday()
    today_date = datetime.now().date()

    yesterday = None
    day_b_yesterday = None

    if week_day == 0 or week_day == 6:
        print('No data')
    elif week_day == 1:
        yesterday = today_date - timedelta(days=1)
        day_b_yesterday = today_date - timedelta(days=4)
    else:
        yesterday = today_date - timedelta(days=1)
        day_b_yesterday = today_date - timedelta(days=2)
    return yesterday, day_b_yesterday


def get_news(date1, date2):
    global COMPANY_NAME

    news_api_key = os.environ["news_key"]
    parameters = {
        "q": COMPANY_NAME,
        "apiKey": news_api_key,
        "language": "en",
        "from": date1,
        "to": date2,
        "sort_by": "relevancy",
        # "country": "us"

    }
    try:
        top_headlines = requests.get("https://newsapi.org/v2/everything", params=parameters)

        headlines = top_headlines.json()
        selected_articles = []
        for article in headlines['articles'][:3]:
            selected_articles.append({
                "title": article['title'],
                "description": article['description']
            })
        return selected_articles
    except:
        return None


def send_text(selected_articles):
    global STOCK
    account_sid = os.environ["sms_sid"]
    auth_token = os.environ["sms_auth"]

    if selected_articles:
        for article in selected_articles:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f"{STOCK}💲💲💲 5%\nTitle: " + article["title"] + "\nDescription: " + article["description"],
                from="+13436553073",
                to="+18259771913",
            )
            print(message.sid)
            print(message.status)
    else:
        client = Client(account_sid, auth_token)
        message = client.messages.create(
            body=f"{STOCK}💲💲💲 5%\nTitle: No recent new found",
            from="+13436553073",
            to="+18259771913",
        )
        print(message.sid)
        print(message.status)


### Start
## STEP 1: Use https://www.alphavantage.co
# When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").

STOCK = "TSLA"
COMPANY_NAME = "Tesla"

# check date
date1, date2 = calculate_dates()
if date1 and date2:
    # Get stock data from API
    data = get_stock_data()
    # Sort socks data
    is_five_percent = get_stock_values(data, date1, date2)
    # Check if there is a variance
    if is_five_percent:
        # Get news from API
        selected_articles = get_news(date1, date2)
        # Send text by API
        send_text(selected_articles)
        print("text sent")
else:
    print("nothing to update")

# Optional: Format the SMS message like this:

# Douglas here - I didn't work on this part as its optional but maybe later xD

"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""
