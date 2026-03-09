from nsepython import *
from tg_sender import send


def options_intelligence(price, macd, signal, pivot, bb_upper, bb_lower):

    # ======================
    # FIND ATM STRIKE
    # ======================

    atm = round(price / 50) * 50


    # ======================
    # GET OPTION CHAIN
    # ======================

    data = nse_optionchain_scrapper("NIFTY")

    records = data['records']['data']

    call_oi = {}
    put_oi = {}

    total_call = 0
    total_put = 0


    for row in records:

        strike = row['strikePrice']

        if row.get("CE"):
            oi = row['CE']['openInterest']
            call_oi[strike] = oi
            total_call += oi

        if row.get("PE"):
            oi = row['PE']['openInterest']
            put_oi[strike] = oi
            total_put += oi


    # ======================
    # FIND SUPPORT / RESISTANCE
    # ======================

    call_resistance = max(call_oi, key=call_oi.get)
    put_support = max(put_oi, key=put_oi.get)

    pcr = round(total_put / total_call, 2)


    # ======================
    # MARKET SCORE
    # ======================

    score = 0

    if macd > signal:
        score += 1

    if price > pivot:
        score += 1

    if price > bb_upper:
        score += 1

    if price < bb_lower:
        score -= 1


    # ======================
    # STRIKE SUGGESTION
    # ======================

    if score >= 2:

        strike = atm + 50
        trade = f"Buy {strike} CE"

    elif score <= -2:

        strike = atm - 50
        trade = f"Buy {strike} PE"

    else:

        trade = "No clear trade"


    # ======================
    # SEND TELEGRAM MESSAGE
    # ======================

    send(f"""
📊 OPTIONS INTELLIGENCE ENGINE

NIFTY : {round(price,2)}

ATM Strike : {atm}

PCR : {pcr}

Strong Resistance : {call_resistance}
Strong Support : {put_support}

Market Score : {score}

Suggested Trade
{trade}
""")