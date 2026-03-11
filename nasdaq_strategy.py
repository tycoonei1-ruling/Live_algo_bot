import yfinance as yf
from tg_sender import send

last_price = None


def monitor_nasdaq():

    global last_price

    df = yf.download("^IXIC", interval="5m", period="1d", progress=False)

    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)

    last = df.iloc[-1]

    price = round(float(last["Close"]),2)

    print("NASDAQ :", price)

    if last_price is None:
        last_price = price
        send(f"📊 NASDAQ Monitoring Started\nBase Price : {price}")
        return

    # 100 point movement alert
    if price >= last_price + 100:

        send(f"""
🚀 NASDAQ UP 100 POINTS

Price : {price}
Previous : {last_price}
""")

        last_price = price

    elif price <= last_price - 100:

        send(f"""
📉 NASDAQ DOWN 100 POINTS

Price : {price}
Previous : {last_price}
""")

        last_price = price