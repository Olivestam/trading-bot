from alpaca.trading.requests import GetOrdersRequest, OrderRequest
from alpaca.trading.enums import OrderSide, OrderType, TimeInForce
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from alpaca.data.live import StockDataStream
from alpaca.data.timeframe import TimeFrame
from ta.volatility import AverageTrueRange
from datetime import datetime, timedelta
from ta.momentum import RSIIndicator
from dotenv import load_dotenv
import xgboost as xgb
import pandas as pd
import numpy as np
import signal
import os

# Holds stock data
global_stock_data = {}
daily_trades = {}   # Holds daily trades for each stock to not be PDT-flagged
# Set up API connection to Alpaca
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
stock_data_stream = StockDataStream(API_KEY, SECRET_KEY)
stock_historical = StockHistoricalDataClient(API_KEY, SECRET_KEY)
trading_client = TradingClient(API_KEY, SECRET_KEY, paper=True)
trading_stream = TradingStream(API_KEY, SECRET_KEY, paper=True)
# Model for prediction
model = xgb.Booster()
model.load_model("data/models/trading_model_2.model")

def handle_data(data):
    print(f"Received data for {data.symbol}: {data.timestamp} - {data.close}")
    global global_stock_data
    if data.symbol not in global_stock_data:
        df = pd.DataFrame([data])
        df = df.map(lambda x: x[1]) 
        df.columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume", "trade_count", "vwap"]
        global_stock_data[data.symbol] = df
    else:
        df = pd.DataFrame([data])
        df = df.map(lambda x: x[1]) 
        df.columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume", "trade_count", "vwap"]
        global_stock_data[data.symbol] = pd.concat([global_stock_data[data.symbol], df], ignore_index=True)
        if len(global_stock_data["SPY"]) > 20 and len(global_stock_data[data.symbol]) > 20:
            df_features = feature_engineering(global_stock_data[data.symbol], global_stock_data["SPY"])
            df_last = df_features.loc[[df_features["timestamp"].idxmax()]]
            trade_decision(df_last)
        
def feature_engineering(df, df_sp):
    # Convert timestamp to Unix time (int64) for efficiency
    df['timestamp'] = pd.to_datetime(df['timestamp'], utc=True).dt.tz_localize(None)
    df['timestamp'] = pd.to_datetime(df['timestamp']).astype('int64') // 10**9
    df_sp['timestamp'] = pd.to_datetime(df_sp['timestamp']).astype('int64') // 10**9
    
    # Sort data by symbol and timestamp
    df = df.sort_values(by=['symbol', 'timestamp'])
    df_sp = df_sp.sort_values(by=['symbol', 'timestamp'])
    
    # Time-based features
    df['hour'] = (df['timestamp'] // 3600) % 24  # Extract hour from timestamp
    df['minute'] = (df['timestamp'] // 60) % 60  # Extract minute from timestamp
    df['day_of_week'] = (df['timestamp'] // 86400) % 7  # Day of the week
    df['is_market_open'] = ((df['hour'] == 9) & (df['minute'] >= 30)) | ((df['hour'] == 10) & (df['minute'] == 0))
    df['is_market_close'] = ((df['hour'] == 15) & (df['minute'] >= 30)) | ((df['hour'] == 16) & (df['minute'] == 0))
    
    # Price change features
    df['log_return'] = np.log(df['close'] / df['close'].shift(1))
    df['volatility'] = df['log_return'].rolling(window=10).std()
    
    # Calculate RSI for each symbol (group by 'symbol')
    rsi = df.groupby('symbol')['close'].apply(lambda x: RSIIndicator(x, window=14).rsi()).reset_index(level=0, drop=True)
    df['rsi'] = rsi

    df['roc'] = df.groupby('symbol')['close'].pct_change(periods=10)
    atr = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
    if isinstance(atr, pd.Series):
        df['atr'] = atr
    else:
        df['atr'] = atr.stack().reset_index(drop=True)
    df['hist_volatility'] = df['log_return'].rolling(20).std()

    # Target variable: price movement in 10 minutes
    df['future_close'] = df.groupby('symbol')['close'].shift(-10)
    threshold = 0.005  # 0.5% change
    df['target'] = np.where(df['future_close'] > (df['close'] * (1 + threshold)), 1, np.where(df['future_close'] < (df['close'] * (1 - threshold)), 2, 0))
    df['target'] = df['target'].astype(np.int8)

    # Add S&P 500 features to the main DataFrame
    df_sp["sp_return_10m"] = df_sp["close"].pct_change(10)
    df_sp["sp_sma"] = df_sp["close"].rolling(window=10).mean()
    df_sp['sp_log_return'] = np.log(df_sp['close'] / df_sp['close'].shift(1))
    df_sp['sp_volatility'] = df_sp['sp_log_return'].rolling(window=10).std()
    df_sp = df_sp[['timestamp', 'sp_return_10m', 'sp_sma', 'sp_volatility', 'sp_log_return']]
    df = df.merge(df_sp, on='timestamp', how='left')
    
    return df.astype({
        'hour': np.int8,
        'minute': np.int8,
        'day_of_week': np.int8,
        'is_market_open': np.int8,
        'is_market_close': np.int8,
        'target': np.int8
    })

# Make predictions using the XGBoost model and take action
def trade_decision(df):
    print(f"Making trade decision for {df.iloc[0]['symbol']}")
    global model
    global trading_client
    symbol = df.iloc[0]['symbol']
    X = df.drop(columns=["target", "symbol", "timestamp", "future_close"])
    data = xgb.DMatrix(X)
    pred_prob = model.predict(data)
    X["prediction"] = np.argmax(pred_prob, axis=1)
    X["confidence"] = np.max(pred_prob, axis=1)
    X['prediction'] = X['prediction'].round().astype(int)
    account_info = trading_client.get_account()
    filter = GetOrdersRequest(side=OrderSide.BUY)
    open_orders = trading_client.get_orders(filter=filter)
    open_orders_price = sum(float(order.qty) * (float(order.limit_price) if order.limit_price else float(order.filled_avg_price)) for order in open_orders)
    if account_info.pattern_day_trader or account_info.account_blocked:
        print("Account is blocked or flagged as pattern day trader")
        stock_data_stream.stop()
    # Check if we should and can buy
    if X.iloc[0]["prediction"] == 1 and X.iloc[0]["confidence"] > 0.85 and daily_trades[symbol] < 3 and account_info.buying_power > ((account_info.equity*0.25) - open_orders_price):
        place_order("buy", symbol, int((account_info.equity*0.25)/df.iloc[0]["close"]))
        daily_trades[symbol] += 1
    positions = trading_client.get_all_positions()
    position_qty = sum(int(position.qty) for position in positions if position.symbol == symbol)
    if X.iloc[0]["prediction"] == 2 and position_qty > 0:
        place_order("sell", symbol, position_qty)
    
# Funktion för att skicka en order
def place_order(order_type, stock, qty):
    if order_type == "buy":
        print("Placing buy order for", stock)
        order_data = OrderRequest(symbol=stock, qty=qty, side=OrderSide.BUY, type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
        trading_client.submit_order(order_data)
    if order_type == "sell":
        print("Placing sell order for", stock)
        order_data = OrderRequest(symbol=stock, qty=qty, side=OrderSide.SELL, type=OrderType.MARKET, time_in_force=TimeInForce.DAY)
        trading_client.submit_order(order_data)

def get_stocks():
    global daily_trades
    file_path = "./data/enriched/enriched__nasdaq100_stocks.parquet"
    df = pd.read_parquet(file_path, engine="pyarrow")
    stocks = df["symbol"].tolist()
    for stock in stocks:
        daily_trades[stock] = 0
    stocks.append("SPY")  # Add S&P 500 ETF to the list of stocks
    return stocks

# Function to get the previous business day
def get_previous_business_day(current_date):
    # If today is Monday, move back to the previous Friday
    if current_date.weekday() == 0:
        return current_date - timedelta(days=3)
    # If today is a weekend (Saturday=5, Sunday=6), move to the previous Friday
    elif current_date.weekday() in [5, 6]:
        return current_date - timedelta(days=(current_date.weekday() - 4))
    else:
        return current_date - timedelta(days=1)

def start_up_data(stock_client, stocks):
    global global_stock_data
    end_date = get_previous_business_day(datetime.now())
    start_date = end_date - timedelta(days=1)
    for stock in stocks:
        request_params = StockBarsRequest(symbol_or_symbols=[stock], timeframe=TimeFrame.Minute, start=start_date, end=end_date)
        bars = stock_client.get_stock_bars(request_params)
        if (stock in bars.data):
            df = pd.DataFrame(bars[stock])
            df = df.map(lambda x: x[1]) 
            df.columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume", "trade_count", "vwap"]
            if not df.empty and not df.isna().all().all():
                global_stock_data[stock] = df

# Handler for when stock data is received from the WebSocket
async def stock_data_handler(data):
    handle_data(data)

async def trade_update_handler(data):
    print(f"Trade update received: {data}")

def run_trading_bot():
    global stock_data_stream
    global stock_historical
    # Set which stocks to trade
    stocks = get_stocks()

    # Add startup data
    print("Loading startup data...")
    start_up_data(stock_historical, stocks)
    print("Startup data loaded")

    # Handle shutdown with CTRL+C
    def signal_handler(sig, frame):
        print("Stopping trading bot...")
        stock_data_stream.stop()
        trading_stream.stop()
        exit(0)
    signal.signal(signal.SIGINT, signal_handler)

    print("Starting trading bot...")
    stock_data_stream.subscribe_bars(stock_data_handler, *stocks)
    trading_stream.subscribe_trade_updates(trade_update_handler)
    try:
        stock_data_stream.run() 
        trading_stream.run()
    except Exception as e:
        print(f"WebSocket error: {e}")
        stock_data_stream.stop()

if __name__ == "__main__":
    run_trading_bot()
