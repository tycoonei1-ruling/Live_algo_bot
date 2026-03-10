from nsepython import *
from tg_sender import send


def analyze_option_chain(records=None):

    if records is None:
        data = nse_optionchain_scrapper("NIFTY")
        records = data['records']['data']

    call_oi = {}
    put_oi = {}

    total_call_oi = 0
    total_put_oi = 0

    for row in records:

        strike = row['strikePrice']

        if row.get("CE"):
            ce_oi = row['CE']['openInterest']
            call_oi[strike] = ce_oi
            total_call_oi += ce_oi

        if row.get("PE"):
            pe_oi = row['PE']['openInterest']
            put_oi[strike] = pe_oi
            total_put_oi += pe_oi


    # Highest OI levels

    max_call = max(call_oi, key=call_oi.get)
    max_put = max(put_oi, key=put_oi.get)

    pcr = round(total_put_oi / total_call_oi, 2)


    send(f"""
📊 NIFTY OPTION CHAIN

PCR : {pcr}

Highest Call OI
Strike : {max_call}

Highest Put OI
Strike : {max_put}

Possible Resistance : {max_call}
Possible Support : {max_put}
""")