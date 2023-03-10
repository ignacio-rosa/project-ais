import yfinance as yf
import yahoo_fin.stock_info as si
import pandas as pd
import pandas_ta as ta
import numpy as np
from math import ceil
from datetime import datetime as dt

def get_data():
    # in process ....
    ticker_list = si.tickers_sp500()
    # sp500 = pd.DataFrame()
    sp500 = []
    for ticker in ticker_list:
        sp = yf.download(ticker, interval='1wk',start="2013-01-01")
        sp['ticker'] = ticker
        sp['index'] = sp.index
        # sp500 = pd.concat([sp500,sp])
        sp500.append(sp)
    return sp500

def update_data():
    ticker_list = si.tickers_sp500()
    sp500 = pd.DataFrame()
    for ticker in ticker_list:
        sp = yf.download(ticker, interval='1wk',start="2013-01-01")
        sp['ticker'] = ticker
        sp['index'] = sp.index
        sp500 = pd.concat([sp500,sp])
    return sp500
    
def week_of_month(dt):
    first_day = dt.replace(day=1)
    dom = dt.day
    adjusted_dom = dom + first_day.weekday()
    return int(ceil(adjusted_dom/7.0))

def add_dates(dataframe):
    df =dataframe.copy()
    df = df.set_index('index')
    df.index = pd.to_datetime(df.index)
    df['year'] = df.index.year
    df['month'] = df.index.month
    df['week_year'] = df.index.week
    df['date'] = pd.to_datetime(df['year'].astype(str) + '-' + df['week_year'].astype(str) + '-1', format='%Y-%W-%w')
    df['week_month'] = df['date'].apply(week_of_month)
    df['week_month'] =df['week_month'] -1
    return df

def add_target(dataframe):
    df =dataframe.copy()
    df['target_reg'] = df['Adj Close'].shift(-1)
    df['target_cla'] = np.where(df['Adj Close'] >= df['target_reg'], 1, 0)

def add_obv(df):
    copy = df.copy()
    copy["OBV"] = (np.sign(copy["Close"].diff()) * copy["Volume"]).fillna(0).cumsum()

    return copy

def add_ema(df):
    copy = df.copy()
    copy['ema'] = copy['Close'].ewm(span=7, adjust=False).mean()

    return copy

def add_rsi(df, periods = 7, ema = True):
    copy = df.copy()
    copy['rsi'] = ta.rsi(df['Close'], length = 7)

    return copy

def add_mcda(df):
    copy = df.copy()
    k = copy['Close'].ewm(span=12, adjust=False, min_periods=12).mean()
    d = copy['Close'].ewm(span=26, adjust=False, min_periods=26).mean()

    macd = k - d
    macd_s = macd.ewm(span=9, adjust=False, min_periods=9).mean()
    macd_h = macd - macd_s
    
    copy['macd'] = macd
    copy['macd_h'] = macd_h
    copy['macd_s'] = macd_s
    
    return copy

def feature_eng(list_df):
    for df_features in list_df:
        df_features = add_dates(df_features)
        df_features = add_obv(df_features)
        df_features = add_ema(df_features)
        df_features = add_rsi(df_features)
        df_features = add_mcda(df_features)
    return list_df

df_list = get_data()
df_list = feature_eng(df_list)
dfs = [df.set_index('id') for df in df_list]
dfs = pd.concat(dfs, axis=1)
dfs.to_csv('sp500_features.csv')