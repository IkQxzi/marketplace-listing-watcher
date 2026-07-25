import requests
from utils.misc import get_text_timestamp

def send_notification(name, url, price, est_profit, webhook_url):
    '''Sends a notification to discord bot
    name = item name
    url = link to ebay listing
    price = price of item
    est_profit = estimated profit from item
    webhook_url = webhook url of discord bot'''

    message = { #message to be sent by bot
        "username": "Alerter",
        "embeds": [
            {
                "title": f"{name}",
                "url": url, 
                "fields": [
                    {"name": "Time", "value": f"{get_text_timestamp()}"},
                    {"name": "Price", "value": f"£{price:.2f}"}, #:.2f tells it to round to float with 2dp
                    {"name": "Estimated profit", "value": f"£{est_profit:.2f}"}
                ],
            }
        ]
    }

    #send message
    response = requests.post(webhook_url, json=message)
    
    if response.status_code == 204:
        print("Sent successfully")
        return True
    else:
        print(f"Fail, status code: {response.status_code}")
        return False
