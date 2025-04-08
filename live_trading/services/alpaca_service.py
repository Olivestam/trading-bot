from alpaca.data.requests import StockBarsRequest
from alpaca.data.timeframe import TimeFrame
from datetime import datetime, timedelta
import pandas as pd

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

def add_historical_data(stock_client, stocks):
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
                # TODO: Add stock data to the global buffer
                global_stock_data[stock] = df