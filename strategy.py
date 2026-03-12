from indicators import get_data, calculate_indicators, calculate_camarilla
from tg_sender import send
from datetime import datetime

base_price = None
triggered_signals = set()

orb_high = None
orb_low = None
orb_set = False

last_status_time = None


def alert_once(signal_id, message):

    if signal_id not in triggered_signals:
        send(message)
        triggered_signals.add(signal_id)


def market_status(price, macd, signal, bb_upper, bb_lower,
                  r1,r2,r3,r4,s1,s2,s3,s4):

    # MACD trend
    macd_trend = "Bullish" if macd > signal else "Bearish"

    # Bollinger status
    if price > bb_upper:
        bb_status = "Upper Breakout"
    elif price < bb_lower:
        bb_status = "Lower Breakdown"
    else:
        bb_status = "Inside Bands"

    # Pivot zone
    if price > r4:
        pivot_zone = "Above R4"
    elif price > r3:
        pivot_zone = "Above R3"
    elif price > r2:
        pivot_zone = "Above R2"
    elif price > r1:
        pivot_zone = "Above R1"
    elif price < s4:
        pivot_zone = "Below S4"
    elif price < s3:
        pivot_zone = "Below S3"
    elif price < s2:
        pivot_zone = "Below S2"
    elif price < s1:
        pivot_zone = "Below S1"
    else:
        pivot_zone = "Between S1 & R1"

    # Overall trend
    if macd > signal and price > r1:
        trend = "Bullish"
    elif macd < signal and price < s1:
        trend = "Bearish"
    else:
        trend = "Sideways"

    return trend, macd_trend, pivot_zone, bb_status


def check_signals():

    global base_price, orb_high, orb_low, orb_set, last_status_time

    df = get_data()
    df = calculate_indicators(df)

    pivot,r1,r2,r3,r4,s1,s2,s3,s4 = calculate_camarilla()

    last = df.iloc[-1]
    prev = df.iloc[-2]

    price = last["Close"]

    macd = last["macd"]
    signal = last["macd_signal"]

    bb_upper = last["bb_upper"]
    bb_middle = last["bb_middle"]
    bb_lower = last["bb_lower"]


    # ==========================
    # MARKET STATUS DASHBOARD
    # ==========================

    now = datetime.now()

    if last_status_time is None or (now - last_status_time).seconds > 3000:

        trend, macd_trend, pivot_zone, bb_status = market_status(
            price, macd, signal, bb_upper, bb_lower,
            r1,r2,r3,r4,s1,s2,s3,s4
        )

        send(f"""
📊 NIFTY MARKET STATUS

Price : {round(price,2)}
Trend : {trend}

MACD : {macd_trend}
Pivot Zone : {pivot_zone}
Bollinger : {bb_status}
""")

        last_status_time = now


    # ==========================
    # 50 POINT TRACKER
    # ==========================

    if base_price is None:

        base_price = round(price / 50) * 50

        send(f"""
📊 BOT STARTED

Starting Level : {base_price}
Current Price : {round(price,2)}
""")


    while price >= base_price + 50:

        base_price += 50

        send(f"""
🚀 NIFTY MOVED UP 50 POINTS

New Level : {base_price}
Current Price : {round(price,2)}
""")


    while price <= base_price - 50:

        base_price -= 50

        send(f"""
📉 NIFTY MOVED DOWN 50 POINTS

New Level : {base_price}
Current Price : {round(price,2)}
""")


    

    # ==========================
    # CAMARILLA LEVEL ALERTS
    # ==========================

    # -------- RESISTANCE --------

    if prev["Close"] <= r1 and price >= r1:
        alert_once("R1_UP", f"🚀 NIFTY crossed above R1 : {r1}")

    if prev["Close"] >= r1 and price <= r1:
        alert_once("R1_DOWN", f"⚠️ NIFTY rejected from R1 : {r1}")


    if prev["Close"] <= r2 and price >= r2:
        alert_once("R2_UP", f"🚀 NIFTY crossed above R2 : {r2}")

    if prev["Close"] >= r2 and price <= r2:
        alert_once("R2_DOWN", f"⚠️ NIFTY rejected from R2 : {r2}")


    if prev["Close"] <= r3 and price >= r3:
        alert_once("R3_UP", f"🔥 NIFTY breakout above R3 : {r3}")

    if prev["Close"] >= r3 and price <= r3:
        alert_once("R3_DOWN", f"⚠️ NIFTY failed at R3 : {r3}")


    if prev["Close"] <= r4 and price >= r4:
        alert_once("R4_UP", f"🔥 STRONG BREAKOUT above R4 : {r4}")

    if prev["Close"] >= r4 and price <= r4:
        alert_once("R4_DOWN", f"⚠️ NIFTY rejected from R4 : {r4}")


    # -------- SUPPORT --------

    if prev["Close"] >= s1 and price <= s1:
        alert_once("S1_DOWN", f"📉 NIFTY broke below S1 : {s1}")

    if prev["Close"] <= s1 and price >= s1:
        alert_once("S1_UP", f"📈 NIFTY recovered above S1 : {s1}")


    if prev["Close"] >= s2 and price <= s2:
        alert_once("S2_DOWN", f"📉 NIFTY broke below S2 : {s2}")

    if prev["Close"] <= s2 and price >= s2:
        alert_once("S2_UP", f"📈 NIFTY recovered above S2 : {s2}")


    if prev["Close"] >= s3 and price <= s3:
        alert_once("S3_DOWN", f"💥 NIFTY breakdown below S3 : {s3}")

    if prev["Close"] <= s3 and price >= s3:
        alert_once("S3_UP", f"🚀 NIFTY bounced above S3 : {s3}")


    if prev["Close"] >= s4 and price <= s4:
        alert_once("S4_DOWN", f"💥 CRASH below S4 : {s4}")

    if prev["Close"] <= s4 and price >= s4:
        alert_once("S4_UP", f"🚀 STRONG BOUNCE above S4 : {s4}")

    # ==========================
    # MACD CROSSOVER
    # ==========================

    if prev["macd"] < prev["macd_signal"] and macd > signal:
        alert_once("MACD_GOLDEN",
                   f"📈 MACD GOLDEN CROSS\nPrice : {round(price,2)}")

    if prev["macd"] > prev["macd_signal"] and macd < signal:
        alert_once("MACD_DEATH",
                   f"📉 MACD DEATH CROSS\nPrice : {round(price,2)}")


    # ==========================
    # BOLLINGER BREAKOUT
    # ==========================

    if price > bb_upper:
        alert_once("BB_UPPER",
                   f"🚀 Bollinger Upper Break\nPrice : {round(price,2)}")

    if price > bb_middle:
        alert_once("BB_MIDDLE",
                   f"📊 Bollinger Middle Break\nPrice : {round(price,2)}")

    if price < bb_lower:
        alert_once("BB_LOWER",
                   f"📉 Bollinger Lower Break\nPrice : {round(price,2)}")


    # ==========================
    # STRONG CONFIRMATION
    # ==========================

    if price > r3 and macd > signal and price > bb_upper:
        alert_once("BULL_CONFIRM",
                   f"🔥 STRONG BULLISH CONFIRMATION\nPrice : {round(price,2)}")

    if price < s3 and macd < signal and price < bb_lower:
        alert_once("BEAR_CONFIRM",
                   f"💥 STRONG BEARISH CONFIRMATION\nPrice : {round(price,2)}")