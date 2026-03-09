import time
from strategy import check_signals

print("Trading Alert Bot Started")

while True:

    check_signals()

    time.sleep(60)

from tg_sender import send
send("Bot started successfully 🚀")