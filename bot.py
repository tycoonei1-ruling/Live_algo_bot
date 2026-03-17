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
india_close_sent = False
last_reset_day = None

# trackers
vix_base = None
gold_base = None
silver_base = None
dxy_base = None
usdinr_base = None


# ==============================
# GLOBAL ASSETS SNAPSHOT
# ==============================

def safe_fetch(symbol):

    try:
        df = yf.download(symbol, period="2d", interval="1d", progress=False)

        if df is None or df.empty:
            return None, None

        if hasattr(df.columns, "levels"):
            df.columns = df.columns.get_level_values(0)

        val = round(df["Close"].iloc[-1], 2)
        chg = round(df["Close"].iloc[-1] - df["Close"].iloc[-2], 2)

        return val, chg

    except:
        return None, None


def global_assets_status():

    try:

        g_v, g_c = safe_fetch("GC=F")
        s_v, s_c = safe_fetch("SI=F")
        d_v, d_c = safe_fetch("DX-Y.NYB")
        i_v, i_c = safe_fetch("USDINR=X")

        def fmt(name, v, c):
            if v is None:
                return f"{name} : NA"
            e = "🟢" if c > 0 else "🔴"
            return f"{name} : {v} {e} ({c})"

        return f"""
🪙 {fmt("GOLD", g_v, g_c)}
🪙 {fmt("SILVER", s_v, s_c)}

💵 {fmt("DXY", d_v, d_c)}
💱 {fmt("USDINR", i_v, i_c)}
"""

    except Exception as e:
        print("Global Assets Error:", e)
        return "Global data unavailable"

# ==============================
# VIX ALERT
# ==============================

def india_vix_monitor():
    global vix_base

    try:
        df = yf.download("^INDIAVIX", interval="5m", period="1d", progress=False)
        if hasattr(df.columns,"levels"):
            df.columns = df.columns.get_level_values(0)

        price = float(df.iloc[-1]["Close"])

        if vix_base is None:
            vix_base = price
            return

        change = ((price - vix_base)/vix_base)*100

        if abs(change) >= 1:
            send(f"⚡ VIX ALERT\n{round(price,2)} ({round(change,2)}%)")
            vix_base = price

    except:
        pass


# ==============================
# GOLD / SILVER ALERT
# ==============================

def gold_silver_monitor():
    global gold_base, silver_base

    try:
        gold = yf.download("GC=F", interval="5m", period="1d", progress=False)
        silver = yf.download("SI=F", interval="5m", period="1d", progress=False)

        for df in [gold,silver]:
            if hasattr(df.columns,"levels"):
                df.columns = df.columns.get_level_values(0)

        g = float(gold.iloc[-1]["Close"])
        s = float(silver.iloc[-1]["Close"])

        if gold_base is None: gold_base = g
        if silver_base is None: silver_base = s

        g_ch = ((g - gold_base)/gold_base)*100
        s_ch = ((s - silver_base)/silver_base)*100

        if abs(g_ch) >= 0.5:
            send(f"🪙 GOLD ALERT\n{round(g,2)} ({round(g_ch,2)}%)")
            gold_base = g

        if abs(s_ch) >= 1:
            send(f"🪙 SILVER ALERT\n{round(s,2)} ({round(s_ch,2)}%)")
            silver_base = s

    except:
        pass


# ==============================
# DXY / USDINR ALERT
# ==============================

def currency_monitor():
    global dxy_base, usdinr_base

    try:
        dxy = yf.download("DX-Y.NYB", interval="5m", period="1d", progress=False)
        inr = yf.download("USDINR=X", interval="5m", period="1d", progress=False)

        for df in [dxy,inr]:
            if hasattr(df.columns,"levels"):
                df.columns = df.columns.get_level_values(0)

        d = float(dxy.iloc[-1]["Close"])
        i = float(inr.iloc[-1]["Close"])

        if dxy_base is None: dxy_base = d
        if usdinr_base is None: usdinr_base = i

        d_ch = ((d - dxy_base)/dxy_base)*100
        i_ch = ((i - usdinr_base)/usdinr_base)*100

        if abs(d_ch) >= 0.5:
            send(f"💵 DXY ALERT\n{round(d,2)} ({round(d_ch,2)}%)")
            dxy_base = d

        if abs(i_ch) >= 0.5:
            send(f"💱 USDINR ALERT\n{round(i,2)} ({round(i_ch,2)}%)")
            usdinr_base = i

    except:
        pass


# ==============================
# GLOBAL MARKET
# ==============================

def global_market_status():

    try:

        assets = global_assets_status()

        dow = yf.download("^DJI", period="2d", interval="1d", progress=False)
        nas = yf.download("^IXIC", period="2d", interval="1d", progress=False)

        for df in [dow,nas]:
            if hasattr(df.columns,"levels"):
                df.columns = df.columns.get_level_values(0)

        d = round(dow["Close"].iloc[-1],2)
        n = round(nas["Close"].iloc[-1],2)

        send(f"""
🌍 GLOBAL MARKET

{assets}

🇺🇸 Dow : {d}
🇺🇸 Nasdaq : {n}
""")

    except:
        pass


# ==============================
# INDIA CLOSE
# ==============================

def india_market_close():

    try:
        nifty = yf.download("^NSEI", period="2d", interval="1d", progress=False)

        if hasattr(nifty.columns,"levels"):
            nifty.columns = nifty.columns.get_level_values(0)

        val = round(nifty["Close"].iloc[-1],2)

        send(f"🇮🇳 INDIA CLOSE\nNIFTY : {val}")

    except:
        pass


# ==============================
# MAIN LOOP
# ==============================

while True:

    try:

        now = datetime.now(ist)
        t = now.time()
        today = now.date()

        if last_reset_day != today:
            morning_sent = europe_sent = india_close_sent = False
            last_reset_day = today

        market_open = datetime.strptime("09:15","%H:%M").time()
        market_close = datetime.strptime("15:30","%H:%M").time()

        if t >= datetime.strptime("08:55","%H:%M").time() and not morning_sent:
            global_market_status()
            morning_sent = True

        if t >= datetime.strptime("15:35","%H:%M").time() and not india_close_sent:
            india_market_close()
            india_close_sent = True

        if market_open <= t <= market_close:

            india_vix_monitor()
            gold_silver_monitor()
            currency_monitor()   # 🔥 NEW
            check_signals()

            time.sleep(60)

        else:
            time.sleep(60)

    except Exception as e:

        err = str(e)
        print("Error:", err)

        if err != last_error:
            send(f"⚠️ Bot Error\n{err}")
            last_error = err

        time.sleep(60)