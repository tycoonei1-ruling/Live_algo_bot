import requests

BOT_TOKEN = "8435744022:AAHlTWFVTqp6Y0ZT0nUUO9Ux8zC_ADKn8y8"
CHAT_ID = "1186459756"

def send(msg):

    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

    payload = {
        "chat_id": CHAT_ID,
        "text": msg
    }

    requests.post(url, data=payload)