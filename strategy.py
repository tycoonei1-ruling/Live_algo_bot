from indicators import get_data, calculate_indicators, calculate_camarilla
from tg_sender import send

base_price = None
triggered_signals = set()


def alert_once(signal_id, message):

    if signal_id not in triggered_signals:
        send(message)
        triggered_signals.add(signal_id)


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
    bb_lower = last["bb_lower"]

    # ==========================
    # 50 POINT MOVE ALERT
    # ==========================

    if base_price is None:
        base_price = price
        send(f"📊 Bot Started\nBase Price : {round(base_price,2)}")

    if price >= base_price + 50:
        alert_once("UP50", f"🚀 NIFTY UP 50 POINTS\nPrice : {round(price,2)}")

    if price <= base_price - 50:
        alert_once("DOWN50", f"📉 NIFTY DOWN 50 POINTS\nPrice : {round(price,2)}")



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