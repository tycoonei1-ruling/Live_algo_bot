import time
from datetime import datetime
import pytz

from strategy import check_signals
from option_chain import analyze_option_chain
from oi_change_detector import detect_oi_change
from tg_sender import send


print("Trading Alert Bot Started")

send("🚀 Trading Alert Bot Started Successfully")


# India timezone
ist = pytz.timezone("Asia/Kolkata")


while True:

    try:

        now = datetime.now(ist)

        current_time = now.time()

        market_open = now.replace(hour=9, minute=15, second=0).time()
        market_close = now.replace(hour=15, minute=30, second=0).time()


        # ==========================
        # MARKET HOURS CHECK
        # ==========================

        if market_open <= current_time <= market_close:

            print("Market Open - Running Bot")

            check_signals()

            analyze_option_chain()

            detect_oi_change()

            time.sleep(60)


        else:

            print("Market Closed - Sleeping")

            time.sleep(900)


    except Exception as e:

        print("Error:", e)

        send(f"⚠️ Bot Error\n{e}")

        time.sleep(60)