import requests

BOT_TOKEN = "8435744022:AAHlTWFVTqp6Y0ZT0nUUO9Ux8zC_ADKn8y8"
CHANNEL_ID = "-1003693434425" # My channel ID from URL


def send(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHANNEL_ID,
        "text": msg
    }

    requests.post(url, data=payload)