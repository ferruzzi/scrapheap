import os
import sys
from datetime import date, datetime, timedelta

import requests

from twilio.rest import Client

# Globals
STOCK = "TSLA"
COMPANY_NAME = "Tesla"


def key_not_found(key_name: str) -> None:
    print(f"{key_name} not found.  Aborting...")
    sys.exit()

def get_stock_data() -> dict[str, str]:
    """Pull data from API."""
    response = requests.get(
        "https://www.alphavantage.co/query",
        params={
            "function": "TIME_SERIES_DAILY",
            "symbol": STOCK,
            "apikey": os.environ.get("stock_key", key_not_found("Alphavantage API Key")),
        }
    )
    return response.json()


def get_stock_values(stock_data: dict[str, str], yesterday_date: date, day_b_yesterday: date) -> bool:
    """
    Get the value from CLOSED
    check if its 5% lower or higher
    if no variance of 5% no more actions required
    """

    yesterday_close = float(stock_data["Time Series (Daily)"][str(yesterday_date)]["4. close"])
    day_b_yesterday_close = float(stock_data["Time Series (Daily)"][str(day_b_yesterday)]["4. close"])
    print(f"##{yesterday_close}")
    print(f"##{day_b_yesterday_close}")

    five_percent_less = day_b_yesterday_close * 0.95
    five_percent_higher = day_b_yesterday_close * 1.05
    print(f"**{five_percent_less}")
    print(f"**{five_percent_higher}")

    if five_percent_less <= yesterday_close <= five_percent_higher:
        print('Get news')
        return True
    else:
        print('Not today!')
        return False


def calculate_dates() -> tuple[date | None, date | None]:
    """
    Here we'll check the dates
    Expect to get update only from last 2 days
    If Monday or Sunday no updates required
    """
    week_day: int = datetime.now().date().weekday()
    today_date: date = datetime.now().date()

    yesterday: date | None = None
    day_b_yesterday: date | None = None

    if week_day in [0, 6]:
        print('No data')
    elif week_day == 1:
        yesterday = today_date - timedelta(days=1)
        day_b_yesterday = today_date - timedelta(days=4)
    else:
        yesterday = today_date - timedelta(days=1)
        day_b_yesterday = today_date - timedelta(days=2)

    return yesterday, day_b_yesterday


def get_news(start_date: date, end_date: date) -> list[dict[str, str]] | None:
    top_headlines = requests.get(
        "https://newsapi.org/v2/everything",
        params={
            "q": COMPANY_NAME,
            "apiKey": os.environ.get("news_key", key_not_found("News API key")),
            "language": "en",
            "from": start_date,
            "to": end_date,
            "sort_by": "relevancy",
            # "country": "us"
        }
    )
    headlines = top_headlines.json()

    try:
        return [
            {"title": article["title"], "description": article["description"]}
            for article in headlines["articles"][:3]
        ]
    except IndexError:
        return None


def send_text(articles: list[dict[str, str]] | None) -> None:
    account_sid = os.environ.get("sms_sid", key_not_found("SMS SID"))
    auth_token = os.environ.get("sms_auth", key_not_found("SMS token"))

    if articles:
        for article in articles:
            client = Client(account_sid, auth_token)
            message = client.messages.create(
                body=f"{STOCK}💲💲💲 5%\nTitle: {article['title']}\nDescription: {article['description']}",
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

# check date
yesterday, previous_day = calculate_dates()
if yesterday and previous_day:
    # Get stock data from API
    data = get_stock_data()
    # Sort data and check if there is a variance
    if get_stock_values(data, yesterday, previous_day):
        # If there is, fetch news and send via SMS
        send_text(get_news(yesterday, previous_day))
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
