from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from alpaca.trading.client import TradingClient
from alpaca.data.live import StockDataStream
import os
import time
from dotenv import load_dotenv
import xgboost as xgb
import pandas as pd
import numpy as np
from datetime import datetime, timedelta

# API-nycklar från Alpaca
load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
wss_client = StockDataStream(API_KEY, SECRET_KEY)

# async handler
async def quote_data_handler(data):
    # quote data will arrive here
    print(data)

wss_client.subscribe_bars(quote_data_handler, "*")

wss_client.run()

""" def get_stock_data(stock, start, end):
    # API-nycklar från Alpaca
    load_dotenv()
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    stock_client = StockHistoricalDataClient(API_KEY,  SECRET_KEY)
    request_params = StockBarsRequest(symbol_or_symbols=[stock], timeframe=TimeFrame.Minute, start=start, end=end)
    bars = stock_client.get_stock_bars(request_params)
    # Flatten the dictionary into a DataFrame
    df = pd.DataFrame(bars[stock])
    # Extrahera endast värdena från tuple-paren
    df = df.map(lambda x: x[1])  # Tar bara det andra elementet i tuple:n
    # Sätt kolumnnamn
    df.columns = ["symbol", "timestamp", "open", "high", "low", "close", "volume", "trade_count", "vwap"]
    return df

def real_time_data(stock):
    # API-nycklar från Alpaca
    load_dotenv()
    API_KEY = os.getenv("ALPACA_API_KEY")
    SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
    stock_stream = StockDataStream(API_KEY, SECRET_KEY)

# Funktion för att göra en prediktion och skicka order
def trade_decision(df):
    # TODO: Implementera prediktion
    print("Trading decision")

# Funktion för att skicka en order
def place_order(order_type):
    # TODO: Implementera order
    print("Placing order")

# Huvudloop för att köra tradingen
def run_trading_bot():
    # Set which stock to trade
    stock = "ERIC"

    # End and Start time
    end_timestamp = datetime.now()  # Now
    start_timestamp = end_timestamp - timedelta(days=1)  # Yesterday

    while True:
        try:
            # Get current time and calculate time to the next whole minute
            now = datetime.now()
            next_minute = (now + timedelta(minutes=1)).replace(second=0, microsecond=0)
            time_to_wait = (next_minute - now).total_seconds()

            # Sleep until the start of the next minute
            print(f"Sleeping for {time_to_wait} seconds until the next full minute.")
            time.sleep(0)

            # Calculate timestamps
            end_timestamp = datetime.now()  # Get the current time
            start_timestamp = end_timestamp - timedelta(days=1)  # Yesterday

            # Get latest data
            df = get_stock_data(stock=stock, start=start_timestamp, end=end_timestamp)
            print(df)
            
            # Make prediction and place order
            trade_decision(df)
        
        except Exception as e:
            print(f"Error: {e}")
            time.sleep(60)  # If there's an error, wait 60 seconds before retrying

if __name__ == "__main__":
    run_trading_bot() """
