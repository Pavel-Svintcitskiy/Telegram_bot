import requests
import pandas as pd

def get_data(symbol='BTCUSDT'):
    url = f'https://api.binance.com/api/v3/klines?symbol={symbol}&interval=1h&limit=100'
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    data = resp.json()
    if not isinstance(data, list) or len(data) == 0:
        raise ValueError("No data returned from Binance API")
    df = pd.DataFrame(data)
    df["close"] = df[4].astype(float)
    return df

def calc_rsi(df, period):
    delta = df['close'].diff()
    gain = delta.where(delta > 0, 0).rolling(period).mean()
    loss = -delta.where(delta < 0, 0).rolling(period).mean()
    rs = gain / loss
    return 100 - (100 / (1 + rs))

def calc_ema(df, period=20):
    return df['close'].ewm(span=period, adjust=False).mean()

def calc_atr(df, period=14):
    df['high'] = df[2].astype(float)
    df['low'] = df[3].astype(float)
    df['close'] = df[4].astype(float)

    df['tr1'] = df['high'] - df['low']
    df['tr2'] = abs(df['high'] - df['close'].shift())
    df['tr3'] = abs(df['low'] - df['close'].shift())

    df['tr'] = df[['tr1', 'tr2', 'tr3']].max(axis=1)


    atr = df['tr'].rolling(window=period).mean()

    return atr

def calc_adx(df, period=14):
    high = df[2].astype(float)
    low = df[3].astype(float)
    close = df[4].astype(float)

    tr1 = high - low
    tr2 = abs(high - close.shift())
    tr3 = abs(low - close.shift())
    tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)

    up_move = high - high.shift()
    down_move = low.shift() - low

    plus_dm = pd.Series(0.0, index=df.index)
    minus_dm = pd.Series(0.0, index=df.index)

    plus_dm[(up_move > down_move) & (up_move > 0)] = up_move
    minus_dm[(down_move > up_move) & (down_move > 0)] = down_move

    atr = tr.rolling(window=period).mean()
    plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
    minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)

    dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

    adx = dx.rolling(window=period).mean()

    return adx, plus_di, minus_di