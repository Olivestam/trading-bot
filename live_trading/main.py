from handlers.data_handler import handle_new_data
from services.alpaca_service import start_data_stream, add_historical_data
from data.buffer import StockDataBuffer
from config import ENV

def main():
    print("Starting trading bot...")
    buffer = StockDataBuffer(maxlen=20)

    if ENV == "dev":
        historical_data = add_historical_data()
        
    start_data_stream(lambda data: handle_new_data(data, buffer))


if __name__ == "__main__":
    main()
