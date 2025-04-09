#from handlers.data_handler import handle_new_data
from services.alpaca_service import add_historical_data, get_stocks
from data.buffer import StockDataBuffer
from config import ENV

def main():
    print("Starting trading bot...")
    buffer = StockDataBuffer(window_size=20)

    stocks = get_stocks()

    if ENV == "dev":
        historical_data = add_historical_data(buffer)
        
    #start_data_stream(lambda data: handle_new_data(data, buffer))


if __name__ == "__main__":
    main()
