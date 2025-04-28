import pandas as pd
import numpy as np
from ta.momentum import RSIIndicator
from ta.volatility import AverageTrueRange

def add_time_features(df):
    df['hour'] = df['timestamp'].dt.hour.astype(np.int8)
    df['minute'] = df['timestamp'].dt.minute.astype(np.int8)
    df['day_of_week'] = df['timestamp'].dt.dayofweek.astype(np.int8)
    df['is_market_open'] = ((df['hour'] == 9) & (df['minute'] >= 30)) | ((df['hour'] == 10) & (df['minute'] == 0))
    df['is_market_close'] = ((df['hour'] == 15) & (df['minute'] >= 30)) | ((df['hour'] == 16) & (df['minute'] == 0))
    return df

def add_technical_indicators(df):
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['volatility'] = df['log_return'].rolling(window=10).std()
    df['rsi'] = df.groupby('symbol')['close'].transform(lambda x: RSIIndicator(x, window=14).rsi())
    df['roc'] = df.groupby('symbol')['close'].pct_change(periods=10)
    df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    df['hist_volatility'] = df['log_return'].rolling(20).std()
    return df

def add_target_variable(df, threshold=0.005):
    df['future_close'] = df.groupby('symbol')['close'].shift(-10)
    df['target'] = np.where(df['future_close'] > df['close'] * (1 + threshold), 1, np.where(df['future_close'] < df['close'] * (1 - threshold), 2, 0))
    df['target'] = df['target'].astype(np.int8)
    return df

def add_sp500_features(df, df_sp):
    df_sp['sp_return_10m'] = df_sp['close'].pct_change(10)
    df_sp['sp_sma'] = df_sp['close'].rolling(window=10).mean()
    df_sp['sp_log_return'] = np.log(df_sp['close'] / df_sp['close'].shift(1))
    df_sp['sp_volatility'] = df_sp['sp_log_return'].rolling(window=10).std()
    
    df = df.merge(
        df_sp[['timestamp', 'sp_return_10m', 'sp_sma', 'sp_volatility', 'sp_log_return']],
        on='timestamp', how='left'
    )
    return df

def feature_engineering(df: pd.DataFrame, df_sp: pd.DataFrame):
    if df.shape[0] < 20 or df_sp.shape[0] < 10:
        raise ValueError("Not enough data to compute features")
    
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)
    df_sp['timestamp'] = pd.to_datetime(df_sp['timestamp'], utc=True).dt.tz_localize(None)
    df = df.sort_values(by=['symbol', 'timestamp'])
    df_sp = df_sp.sort_values(by=['symbol', 'timestamp'])

    df = add_time_features(df)
    df = add_technical_indicators(df)
    df = add_target_variable(df)
    df = add_sp500_features(df, df_sp)

    # Return only latest data
    latest_idx = df['timestamp'].idxmax()
    return df.loc[[latest_idx]]
