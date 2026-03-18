import time
from datetime import datetime
import pytz
import yfinance as yf

from strategy import check_signals
from tg_sender import send

print("Trading Alert Bot Started")
send("🚀 Bot Is Ready")

ist = pytz.timezone("Asia/Kolkata")

last_error = None

# flags
morning_sent = False
europe_sent = False
india_close_sent = False
us_close_sent = False
last_reset_day = None

# trackers
vix_base = None
gold_base = None
silver_base = None
dxy_base = None
usdinr_base = None


# ==============================
# SAFE FETCH
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

# ==============================
# OPENING BELL
# ==============================

def opening_bell():

    try:

        assets = global_assets_status()

        # US markets
        dow_v, dow_c = safe_fetch("^DJI")
        nas_v, nas_c = safe_fetch("^IXIC")
        sp_v, sp_c = safe_fetch("^GSPC")

        # India VIX
        vix_v, vix_c = safe_fetch("^INDIAVIX")

        e = lambda x: "🟢" if x and x > 0 else "🔴"

        send(f"""
🔔 OPENING BELL (PRE-MARKET)

{assets}

📊 INDIA VIX : {vix_v} {e(vix_c)} ({vix_c})

🇺🇸 US MARKETS
Dow : {dow_v} {e(dow_c)} ({dow_c})
Nasdaq : {nas_v} {e(nas_c)} ({nas_c})
S&P 500 : {sp_v} {e(sp_c)} ({sp_c})

Market Opening Soon 🚀
""")

    except Exception as e:
        print("Opening Bell Error:", e)


# ==============================
# GLOBAL ASSETS
# ==============================

def global_assets_status():

    g_v, g_c = safe_fetch("GC=F")
    s_v, s_c = safe_fetch("SI=F")
    d_v, d_c = safe_fetch("DX=F")      # FIXED
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
        dxy = yf.download("DX=F", interval="5m", period="1d", progress=False)
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

    assets = global_assets_status()

    dow_v, dow_c = safe_fetch("^DJI")
    nas_v, nas_c = safe_fetch("^IXIC")

    send(f"""
🌍 GLOBAL MARKET

{assets}

🇺🇸 Dow : {dow_v}
🇺🇸 Nasdaq : {nas_v}
""")


# ==============================
# EUROPE OPEN
# ==============================

def europe_market_status():

    try:

        ft_v, ft_c = safe_fetch("^FTSE")
        dax_v, dax_c = safe_fetch("^GDAXI")
        cac_v, cac_c = safe_fetch("^FCHI")

        e = lambda x: "🟢" if x > 0 else "🔴"

        send(f"""
🇪🇺 EUROPE MARKET OPEN

FTSE 100 : {ft_v} {e(ft_c)} ({ft_c})
DAX : {dax_v} {e(dax_c)} ({dax_c})
CAC 40 : {cac_v} {e(cac_c)} ({cac_c})
""")

    except Exception as e:
        print("Europe Error:", e)


# ==============================
# US CLOSE
# ==============================

def us_market_close():

    try:

        d_v, d_c = safe_fetch("^DJI")
        n_v, n_c = safe_fetch("^IXIC")
        s_v, s_c = safe_fetch("^GSPC")

        e = lambda x: "🟢" if x > 0 else "🔴"

        send(f"""
🇺🇸 US MARKET CLOSE

Dow : {d_v} {e(d_c)} ({d_c})
Nasdaq : {n_v} {e(n_c)} ({n_c})
S&P 500 : {s_v} {e(s_c)} ({s_c})
""")

    except Exception as e:
        print("US Close Error:", e)


# ==============================
# INDIA CLOSE
# ==============================

def india_market_close():

    try:

        n_v, n_c = safe_fetch("^NSEI")
        g_v, _ = safe_fetch("GC=F")
        s_v, _ = safe_fetch("SI=F")

        e = "🟢" if n_c > 0 else "🔴"

        send(f"""
🇮🇳 INDIA CLOSE

NIFTY : {n_v} {e} ({n_c})

🪙 GOLD : {g_v}
🪙 SILVER : {s_v}
""")

    except Exception as e:
        print("India Close Error:", e)


# ==============================
# MAIN LOOP
# ==============================

while True:

    try:

        now = datetime.now(ist)
        t = now.time()
        today = now.date()

        if last_reset_day != today:
            morning_sent = europe_sent = india_close_sent = us_close_sent = False
            last_reset_day = today

        market_open = datetime.strptime("09:15","%H:%M").time()
        market_close = datetime.strptime("15:30","%H:%M").time()

        # MORNING
        if t >= datetime.strptime("08:55","%H:%M").time() and not morning_sent:
            opening_bell()
            morning_sent = True

        # EUROPE
        if t >= datetime.strptime("12:45","%H:%M").time() and t <= datetime.strptime("13:30","%H:%M").time() and not europe_sent:
            europe_market_status()
            europe_sent = True

        # INDIA CLOSE
        if t >= datetime.strptime("15:35","%H:%M").time() and not india_close_sent:
            india_market_close()
            india_close_sent = True

        # US CLOSE
        if t >= datetime.strptime("02:10","%H:%M").time() and t <= datetime.strptime("03:00","%H:%M").time() and not us_close_sent:
            us_market_close()
            us_close_sent = True

        # MARKET HOURS
        if market_open <= t <= market_close:

            india_vix_monitor()
            gold_silver_monitor()
            currency_monitor()
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