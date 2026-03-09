import pandas as pd
import yfinance as yf
from ta.volatility import BollingerBands
from ta.trend import MACD

def get_data():

    df = yf.download("^NSEI", interval="15m", period="5d", auto_adjust=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    return df

    # flatten multi-index columns if present
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    return df


def calculate_indicators(df):

    close = df["Close"]

    # ==============================
    # BOLLINGER BANDS
    # ==============================

    bb = BollingerBands(close=close, window=20, window_dev=2)

    df["bb_upper"] = bb.bollinger_hband()
    df["bb_middle"] = bb.bollinger_mavg()
    df["bb_lower"] = bb.bollinger_lband()

    # ==============================
    # MACD
    # ==============================

    macd = MACD(close=close, window_slow=26, window_fast=12, window_sign=9)

    df["macd"] = macd.macd()
    df["macd_signal"] = macd.macd_signal()

    return df


import yfinance as yf
import pandas as pd


def calculate_camarilla():

    df = yf.download("^NSEI", interval="1d", period="7d", progress=False)

    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.dropna()

    prev = df.iloc[-2]

    high = float(prev["High"])
    low = float(prev["Low"])
    close = float(prev["Close"])

    rng = high - low

    pivot = (high + low + close) / 3

    r1 = close + (rng * 1.1 / 12)
    r2 = close + (rng * 1.1 / 6)
    r3 = close + (rng * 1.1 / 4)
    r4 = close + (rng * 1.1 / 2)

    s1 = close - (rng * 1.1 / 12)
    s2 = close - (rng * 1.1 / 6)
    s3 = close - (rng * 1.1 / 4)
    s4 = close - (rng * 1.1 / 2)

    return round(pivot),round(r1),round(r2),round(r3),round(r4),round(s1),round(s2),round(s3),round(s4)