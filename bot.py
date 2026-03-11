import time
from datetime import datetime
import pytz
import yfinance as yf

from strategy import check_signals
from tg_sender import send


print("Trading Alert Bot Started")
send("🚀 Bot Is Ready")

# timezone
ist = pytz.timezone("Asia/Kolkata")

last_error = None

# prevent duplicate alerts
morning_sent = False
europe_sent = False
us_close_sent = False
last_reset_day = None


# ==============================
# GLOBAL MARKET STATUS
# ==============================

def global_market_status():

    try:

        dow = yf.download("^DJI", period="2d", interval="1d", progress=False)
        nasdaq = yf.download("^IXIC", period="2d", interval="1d", progress=False)
        sp = yf.download("^GSPC", period="2d", interval="1d", progress=False)

        nikkei = yf.download("^N225", period="2d", interval="1d", progress=False)
        hang = yf.download("^HSI", period="2d", interval="1d", progress=False)
        shanghai = yf.download("000001.SS", period="2d", interval="1d", progress=False)

        for df in [dow, nasdaq, sp, nikkei, hang, shanghai]:
            if hasattr(df.columns, "levels"):
                df.columns = df.columns.get_level_values(0)

        if len(dow) < 2 or len(nasdaq) < 2 or len(sp) < 2:
            print("Market data unavailable")
            return

        dow_value = round(dow["Close"].iloc[-1],2)
        dow_change = round(dow["Close"].iloc[-1] - dow["Close"].iloc[-2],2)

        nasdaq_value = round(nasdaq["Close"].iloc[-1],2)
        nasdaq_change = round(nasdaq["Close"].iloc[-1] - nasdaq["Close"].iloc[-2],2)

        sp_value = round(sp["Close"].iloc[-1],2)
        sp_change = round(sp["Close"].iloc[-1] - sp["Close"].iloc[-2],2)

        nikkei_value = round(nikkei["Close"].iloc[-1],2)
        nikkei_change = round(nikkei["Close"].iloc[-1] - nikkei["Close"].iloc[-2],2)

        hang_value = round(hang["Close"].iloc[-1],2)
        hang_change = round(hang["Close"].iloc[-1] - hang["Close"].iloc[-2],2)

        shanghai_value = round(shanghai["Close"].iloc[-1],2)
        shanghai_change = round(shanghai["Close"].iloc[-1] - shanghai["Close"].iloc[-2],2)

        dow_emoji = "🟢" if dow_change > 0 else "🔴"
        nasdaq_emoji = "🟢" if nasdaq_change > 0 else "🔴"
        sp_emoji = "🟢" if sp_change > 0 else "🔴"

        nikkei_emoji = "🟢" if nikkei_change > 0 else "🔴"
        hang_emoji = "🟢" if hang_change > 0 else "🔴"
        shanghai_emoji = "🟢" if shanghai_change > 0 else "🔴"

        send(f"""
🌍 GLOBAL MARKET UPDATE

🇺🇸 US MARKETS
Dow Jones : {dow_value} {dow_emoji} ({dow_change})
Nasdaq : {nasdaq_value} {nasdaq_emoji} ({nasdaq_change})
S&P 500 : {sp_value} {sp_emoji} ({sp_change})

🌏 ASIAN MARKETS
Nikkei : {nikkei_value} {nikkei_emoji} ({nikkei_change})
Hang Seng : {hang_value} {hang_emoji} ({hang_change})
Shanghai : {shanghai_value} {shanghai_emoji} ({shanghai_change})
""")

    except Exception as e:
        print("Global Market Error:", e)


# ==============================
# EUROPE MARKET OPEN
# ==============================

def europe_market_status():

    try:

        ftse = yf.download("^FTSE", period="2d", interval="1d", progress=False)
        dax = yf.download("^GDAXI", period="2d", interval="1d", progress=False)
        cac = yf.download("^FCHI", period="2d", interval="1d", progress=False)

        for df in [ftse, dax, cac]:
            if hasattr(df.columns, "levels"):
                df.columns = df.columns.get_level_values(0)

        if len(ftse) < 2 or len(dax) < 2 or len(cac) < 2:
            return

        ftse_value = round(ftse["Close"].iloc[-1],2)
        ftse_change = round(ftse["Close"].iloc[-1] - ftse["Close"].iloc[-2],2)

        dax_value = round(dax["Close"].iloc[-1],2)
        dax_change = round(dax["Close"].iloc[-1] - dax["Close"].iloc[-2],2)

        cac_value = round(cac["Close"].iloc[-1],2)
        cac_change = round(cac["Close"].iloc[-1] - cac["Close"].iloc[-2],2)

        ftse_emoji = "🟢" if ftse_change > 0 else "🔴"
        dax_emoji = "🟢" if dax_change > 0 else "🔴"
        cac_emoji = "🟢" if cac_change > 0 else "🔴"

        send(f"""
🇪🇺 EUROPE MARKET OPEN

FTSE 100 : {ftse_value} {ftse_emoji} ({ftse_change})
DAX : {dax_value} {dax_emoji} ({dax_change})
CAC 40 : {cac_value} {cac_emoji} ({cac_change})
""")

    except Exception as e:
        print("Europe Market Error:", e)


# ==============================
# US MARKET CLOSE UPDATE
# ==============================

def us_market_close():

    try:

        dow = yf.download("^DJI", period="2d", interval="1d", progress=False)
        nasdaq = yf.download("^IXIC", period="2d", interval="1d", progress=False)
        sp = yf.download("^GSPC", period="2d", interval="1d", progress=False)

        for df in [dow, nasdaq, sp]:
            if hasattr(df.columns, "levels"):
                df.columns = df.columns.get_level_values(0)

        if len(dow) < 2 or len(nasdaq) < 2 or len(sp) < 2:
            return

        dow_close = round(dow["Close"].iloc[-1],2)
        dow_change = round(dow["Close"].iloc[-1] - dow["Close"].iloc[-2],2)

        nasdaq_close = round(nasdaq["Close"].iloc[-1],2)
        nasdaq_change = round(nasdaq["Close"].iloc[-1] - nasdaq["Close"].iloc[-2],2)

        sp_close = round(sp["Close"].iloc[-1],2)
        sp_change = round(sp["Close"].iloc[-1] - sp["Close"].iloc[-2],2)

        dow_emoji = "🟢" if dow_change > 0 else "🔴"
        nasdaq_emoji = "🟢" if nasdaq_change > 0 else "🔴"
        sp_emoji = "🟢" if sp_change > 0 else "🔴"

        send(f"""
🇺🇸 US MARKET CLOSE

Dow Jones : {dow_close} {dow_emoji} ({dow_change})
Nasdaq : {nasdaq_close} {nasdaq_emoji} ({nasdaq_change})
S&P 500 : {sp_close} {sp_emoji} ({sp_change})

Session Closed 📉
""")

    except Exception as e:
        print("US Market Close Error:", e)


# ==============================
# NASDAQ TEST MONITOR
# ==============================

nasdaq_base_price = None

def nasdaq_monitor():

    global nasdaq_base_price

    try:

        df = yf.download("^IXIC", interval="5m", period="1d", progress=False)

        if hasattr(df.columns, "levels"):
            df.columns = df.columns.get_level_values(0)

        last = df.iloc[-1]
        price = round(float(last["Close"]),2)

        print("NASDAQ :", price)

        if nasdaq_base_price is None:

            nasdaq_base_price = price

            send(f"""
📊 NASDAQ TEST MODE STARTED

Base Price : {price}
Monitoring 100 point movement
""")

            return

        if price >= nasdaq_base_price + 100:

            send(f"""
🚀 NASDAQ UP 100 POINTS

Price : {price}
Previous Base : {nasdaq_base_price}
""")

            nasdaq_base_price = price

        elif price <= nasdaq_base_price - 100:

            send(f"""
📉 NASDAQ DOWN 100 POINTS

Price : {price}
Previous Base : {nasdaq_base_price}
""")

            nasdaq_base_price = price

    except Exception as e:
        print("NASDAQ Error:", e)


# ==============================
# MAIN LOOP
# ==============================

while True:

    try:

        now = datetime.now(ist)
        current_time = now.time()
        today = now.date()

        if last_reset_day != today:
            morning_sent = False
            europe_sent = False
            us_close_sent = False
            last_reset_day = today

        market_open = datetime.strptime("09:15", "%H:%M").time()
        market_close = datetime.strptime("15:30", "%H:%M").time()

        us_close_time = datetime.strptime("02:10", "%H:%M").time()

        if current_time >= us_close_time and not us_close_sent:
            us_market_close()
            us_close_sent = True

        if current_time >= datetime.strptime("08:55", "%H:%M").time() and not morning_sent:
            global_market_status()
            morning_sent = True

        if current_time >= datetime.strptime("12:45", "%H:%M").time() and not europe_sent:
            europe_market_status()
            europe_sent = True

        if market_open <= current_time <= market_close:

            print("Market Open - Running Bot")
            check_signals()
            time.sleep(60)

        else:

            print("Market Closed - Running NASDAQ Test")
            nasdaq_monitor()
            time.sleep(60)

    except Exception as e:

        error_msg = str(e)

        print("Error:", error_msg)

        if error_msg != last_error:
            send(f"⚠️ Bot Error\n{error_msg}")
            last_error = error_msg

        time.sleep(60)