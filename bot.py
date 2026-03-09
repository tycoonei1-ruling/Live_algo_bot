import time

from strategy import check_signals
from option_chain import analyze_option_chain
from oi_change_detector import detect_oi_change
from tg_sender import send


print("Trading Alert Bot Started")

# Send startup message to Telegram
send("🚀 Trading Alert Bot Started Successfully")


while True:

    try:

        # Run strategy alerts
        check_signals()

        # Run option chain analyzer
        analyze_option_chain()

        # Run OI change detector
        detect_oi_change()

    except Exception as e:

        print("Error:", e)

        send(f"⚠️ Bot Error\n{e}")

    # wait before next cycle
    time.sleep(60)