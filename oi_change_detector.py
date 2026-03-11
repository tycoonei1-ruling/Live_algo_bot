from nsepython import *
from tg_sender import send

previous_oi = {}


def detect_oi_change():

    global previous_oi

    data = nse_optionchain_scrapper("NIFTY")

    records = data['records']['data']

    signals = []

    for row in records:

        strike = row['strikePrice']

        if row.get("CE"):

            ce_oi = row['CE']['openInterest']
            ce_ltp = row['CE']['lastPrice']

            key = f"{strike}_CE"

            if key in previous_oi:

                prev_oi = previous_oi[key]["oi"]
                prev_price = previous_oi[key]["price"]

                if ce_ltp > prev_price and ce_oi > prev_oi:
                    signals.append(f"{strike} CE → LONG BUILDUP")

                elif ce_ltp < prev_price and ce_oi > prev_oi:
                    signals.append(f"{strike} CE → SHORT BUILDUP")

                elif ce_ltp > prev_price and ce_oi < prev_oi:
                    signals.append(f"{strike} CE → SHORT COVERING")

                elif ce_ltp < prev_price and ce_oi < prev_oi:
                    signals.append(f"{strike} CE → LONG UNWINDING")

            previous_oi[key] = {"oi": ce_oi, "price": ce_ltp}


        if row.get("PE"):

            pe_oi = row['PE']['openInterest']
            pe_ltp = row['PE']['lastPrice']

            key = f"{strike}_PE"

            if key in previous_oi:

                prev_oi = previous_oi[key]["oi"]
                prev_price = previous_oi[key]["price"]

                if pe_ltp > prev_price and pe_oi > prev_oi:
                    signals.append(f"{strike} PE → LONG BUILDUP")

                elif pe_ltp < prev_price and pe_oi > prev_oi:
                    signals.append(f"{strike} PE → SHORT BUILDUP")

                elif pe_ltp > prev_price and pe_oi < prev_oi:
                    signals.append(f"{strike} PE → SHORT COVERING")

                elif pe_ltp < prev_price and pe_oi < prev_oi:
                    signals.append(f"{strike} PE → LONG UNWINDING")

            previous_oi[key] = {"oi": pe_oi, "price": pe_ltp}


    if signals:

        message = "\n".join(signals[:5])

        send(f"""
⚡ OI CHANGE DETECTED

{message}
""")