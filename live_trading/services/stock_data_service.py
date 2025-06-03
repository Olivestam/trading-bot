from handlers.data_handler import handle_new_bar, process_bars
from alpaca.data import StockHistoricalDataClient
from alpaca.data.requests import StockBarsRequest
from alpaca.data.live import StockDataStream
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
from config import API_KEY, SECRET_KEY
from data.buffer import buffer
import pandas as pd
import asyncio

def get_previous_business_day(current_date):
    if current_date.weekday() == 0: # If today is Monday, move back to the previous Friday
        return current_date - timedelta(days=3)
    elif current_date.weekday() in [5, 6]:  # If today is a weekend (Saturday=5, Sunday=6), move to the previous Friday
        return current_date - timedelta(days=(current_date.weekday() - 4))
    else:
        return current_date - timedelta(days=1)
    
def get_stocks():
    file_path = "../data/enriched/enriched__nasdaq100_stocks.parquet"
    df = pd.read_parquet(file_path, engine="pyarrow")
    stocks = df["symbol"].tolist()
    stocks.append("SPY")  # Add S&P 500 ETF to the list of stocks, (used for creating features)
    return stocks

def add_historical_data():
    print("Loading historical data...")
    stock_client = StockHistoricalDataClient(API_KEY, SECRET_KEY)
    end_date = get_previous_business_day(datetime.now())
    start_date = end_date - timedelta(days=1)
    stocks = get_stocks()
    for stock in stocks:
        request_params = StockBarsRequest(symbol_or_symbols=[stock], timeframe=TimeFrame.Minute, start=start_date, end=end_date)
        bars = stock_client.get_stock_bars(request_params)
        if (stock in bars.data):
            for bar in bars[stock]:
                buffer.add(stock, bar)

async def start_data_stream():
    print("Starting stream...")
    stream = StockDataStream(API_KEY, SECRET_KEY)
    stocks = get_stocks()
    stream.subscribe_bars(handle_new_bar, *stocks)
    asyncio.create_task(process_bars())
    await stream._run_forever()