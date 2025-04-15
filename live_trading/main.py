from services.alpaca_service import add_historical_data, start_data_stream
from config import ENV
import asyncio

def main():
    if ENV == "dev":
        add_historical_data()

    asyncio.run(start_data_stream())
if __name__ == "__main__":
    main()
