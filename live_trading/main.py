from services.stock_data_service import add_historical_data, start_data_stream
from services.trading_service import start_trading_stream
from services.trading_service import get_account_info
from config import ENV
import asyncio

async def main_async():
    if ENV == "dev":
        add_historical_data()
    
    # Create tasks for both streams to run concurrently
    data_stream_task = asyncio.create_task(start_data_stream())
    trading_stream_task = asyncio.create_task(start_trading_stream())
    
    # Wait for both tasks to complete (they won't normally complete)
    await asyncio.gather(data_stream_task, trading_stream_task)

def main():
    asyncio.run(main_async())

if __name__ == "__main__":
    main()

# Next task:
# - Add lock to buy_tracker to prevent multiple read/write operations at the same time
