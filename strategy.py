from indicators import get_data, calculate_indicators, calculate_camarilla
from tg_sender import send
from options_intelligence import options_intelligence

base_price = None
triggered_signals = set()


def alert_once(signal_id, message):

    if signal_id not in triggered_signals:
        send(message)
        triggered_signals.add(signal_id)

from datetime import datetime

orb_high = None
orb_low = None
orb_set = False

def check_signals():

    global base_price

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

    options_intelligence(price, macd, signal, pivot, bb_upper, bb_lower)

from datetime import datetime

def market_status(price, macd, signal, bb_upper, bb_lower,
                  r1,r2,r3,r4,s1,s2,s3,s4):

    # MACD trend
    if macd > signal:
        macd_trend = "Bullish"
    else:
        macd_trend = "Bearish"

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

    # ==========================
    # MARKET STATUS DASHBOARD
    # ==========================

    global last_status_time

    now = datetime.now()

    if last_status_time is None or (now - last_status_time).seconds > 300:

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
    # PROFESSIONAL 50 POINT TRACKER
    # ==========================

    if base_price is None:
        base_price = round(price / 50) * 50
        send(f"""
    📊 BOT STARTED

    Starting Level : {base_price}
    Current Price : {round(price,2)}
    """)


    # MARKET MOVING UP
    while price >= base_price + 50:

        base_price += 50

        send(f"""
    🚀 NIFTY MOVED UP 50 POINTS

    New Level : {base_price}
    Current Price : {round(price,2)}
    """)


    # MARKET MOVING DOWN
    while price <= base_price - 50:

        base_price -= 50

        send(f"""
    📉 NIFTY MOVED DOWN 50 POINTS

    New Level : {base_price}
    Current Price : {round(price,2)}
    """)

    # ==========================
    # OPENING RANGE BREAKOUT
    # ==========================

    global orb_high, orb_low, orb_set

    now = datetime.now()

    # Capture opening range (9:15–9:30)

    if now.hour == 9 and now.minute < 30:

        if orb_high is None or price > orb_high:
            orb_high = price

        if orb_low is None or price < orb_low:
            orb_low = price


    # Lock the range at 9:30

    if now.hour == 9 and now.minute >= 30 and not orb_set:

        orb_set = True

        send(f"""
    📊 OPENING RANGE SET

    ORB High : {round(orb_high,2)}
    ORB Low : {round(orb_low,2)}
    """)



    # Breakout detection

    if orb_set:

        if price > orb_high:

            send(f"""
    🚀 ORB BREAKOUT

    Price broke above opening range

    Price : {round(price,2)}
    ORB High : {round(orb_high,2)}
    """)

            orb_set = False


        if price < orb_low:

            send(f"""
    📉 ORB BREAKDOWN

    Price broke below opening range

    Price : {round(price,2)}
    ORB Low : {round(orb_low,2)}
    """)

            orb_set = False

    # ==========================
    # CAMARILLA RESISTANCE
    # ==========================

    if prev["Close"] < r1 and price > r1:
        alert_once("R1", f"⚡ NIFTY crossed R1 : {r1}")

    if prev["Close"] < r2 and price > r2:
        alert_once("R2", f"⚡ NIFTY crossed R2 : {r2}")

    if prev["Close"] < r3 and price > r3:
        alert_once("R3", f"🚀 NIFTY crossed R3 : {r3}")

    if prev["Close"] < r4 and price > r4:
        alert_once("R4", f"🔥 NIFTY crossed R4 : {r4}")


    # ==========================
    # CAMARILLA SUPPORT
    # ==========================

    if prev["Close"] > s1 and price < s1:
        alert_once("S1", f"⚡ NIFTY crossed S1 : {s1}")

    if prev["Close"] > s2 and price < s2:
        alert_once("S2", f"⚡ NIFTY crossed S2 : {s2}")

    if prev["Close"] > s3 and price < s3:
        alert_once("S3", f"📉 NIFTY crossed S3 : {s3}")

    if prev["Close"] > s4 and price < s4:
        alert_once("S4", f"💥 NIFTY crossed S4 : {s4}")


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
                   f"📉 Bollinger Middle Break\nPrice : {round(price,2)}")             

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

    # ==========================
    # OPTIONS MOMENTUM DETECTION
    # ==========================

    # CALL SIDE MOMENTUM

    if price > r3 and macd > signal and price > bb_upper:

        send(f"""
    🚀 CALL SIDE MOMENTUM

    NIFTY ABOVE R3
    MACD BULLISH
    BOLLINGER BREAKOUT

    Price : {round(price,2)}

    Possible CE Momentum
    """)


    # PUT SIDE MOMENTUM

    if price < s3 and macd < signal and price < bb_lower:

        send(f"""
    📉 PUT SIDE MOMENTUM

    NIFTY BELOW S3
    MACD BEARISH
    BOLLINGER BREAKDOWN

    Price : {round(price,2)}

    Possible PE Momentum
    """)