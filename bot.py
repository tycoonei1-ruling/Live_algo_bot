import time
from datetime import datetime
import pytz
import yfinance as yf

from strategy import check_signals
from tg_sender import send


print("Trading Alert Bot Started")

send("🚀 Trading Alert Bot Started Successfully")


# timezone
ist = pytz.timezone("Asia/Kolkata")

last_error = None

# prevent duplicate alerts
morning_sent = False
europe_sent = False


# ==============================
# GLOBAL MARKET STATUS
# ==============================

def global_market_status():

    try:

        dow = yf.download("^DJI", period="2d", interval="1d", progress=False)
        nasdaq = yf.download("^IXIC", period="2d", interval="1d", progress=False)
        sp = yf.download("^GSPC", period="2d", interval="1d", progress=False)

        nikkei = yf.download("^N225", period="1d", interval="1d", progress=False)
        hang = yf.download("^HSI", period="1d", interval="1d", progress=False)
        shanghai = yf.download("000001.SS", period="1d", interval="1d", progress=False)

        dow_change = round(dow["Close"].iloc[-1] - dow["Open"].iloc[-1],2)
        nasdaq_change = round(nasdaq["Close"].iloc[-1] - nasdaq["Open"].iloc[-1],2)
        sp_change = round(sp["Close"].iloc[-1] - sp["Open"].iloc[-1],2)

        nikkei_change = round(nikkei["Close"].iloc[-1] - nikkei["Open"].iloc[-1],2)
        hang_change = round(hang["Close"].iloc[-1] - hang["Open"].iloc[-1],2)
        shanghai_change = round(shanghai["Close"].iloc[-1] - shanghai["Open"].iloc[-1],2)


        send(f"""
🌍 GLOBAL MARKET UPDATE

🇺🇸 US MARKETS (Previous Close)

Dow Jones : {dow_change}
Nasdaq : {nasdaq_change}
S&P 500 : {sp_change}

🌏 ASIAN MARKETS

Nikkei : {nikkei_change}
Hang Seng : {hang_change}
Shanghai : {shanghai_change}
""")

    except Exception as e:

        print("Global Market Error:", e)



# ==============================
# EUROPE MARKET OPEN
# ==============================

def europe_market_status():

    try:

        ftse = yf.download("^FTSE", period="1d", interval="1d", progress=False)
        dax = yf.download("^GDAXI", period="1d", interval="1d", progress=False)
        cac = yf.download("^FCHI", period="1d", interval="1d", progress=False)

        ftse_change = round(ftse["Close"].iloc[-1] - ftse["Open"].iloc[-1],2)
        dax_change = round(dax["Close"].iloc[-1] - dax["Open"].iloc[-1],2)
        cac_change = round(cac["Close"].iloc[-1] - cac["Open"].iloc[-1],2)


        send(f"""
🇪🇺 EUROPE MARKET OPEN

FTSE 100 : {ftse_change}
DAX : {dax_change}
CAC 40 : {cac_change}
""")

    except Exception as e:

        print("Europe Market Error:", e)



# ==============================
# MAIN LOOP
# ==============================

while True:

    try:

        now = datetime.now(ist)

        current_time = now.time()

        market_open = datetime.strptime("09:15", "%H:%M").time()
        market_close = datetime.strptime("15:30", "%H:%M").time()

        global morning_sent
        global europe_sent


        # ==========================
        # GLOBAL MARKET UPDATE 8:55
        # ==========================

        if current_time >= datetime.strptime("08:55","%H:%M").time() and not morning_sent:

            global_market_status()

            morning_sent = True


        # ==========================
        # EUROPE MARKET UPDATE 12:45
        # ==========================

        if current_time >= datetime.strptime("12:45","%H:%M").time() and not europe_sent:

            europe_market_status()

            europe_sent = True


        # ==========================
        # TRADING BOT
        # ==========================

        if market_open <= current_time <= market_close:

            print("Market Open - Running Bot")

            check_signals()

            time.sleep(60)

        else:

            print("Market Closed - Sleeping")

            time.sleep(300)


    except Exception as e:

        error_msg = str(e)

        print("Error:", error_msg)

        if error_msg != last_error:

            send(f"⚠️ Bot Error\n{error_msg}")

            last_error = error_msg

        time.sleep(60)