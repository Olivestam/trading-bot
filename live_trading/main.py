from services.alpaca_service import add_historical_data, start_data_stream
from config import ENV
import asyncio

def main():
    print("Starting trading bot...")
    """ if ENV == "dev":
        add_historical_data() """
    # Om ingen loop är igång, skapa en ny loop
    try:
        loop = asyncio.get_event_loop()
        loop.create_task(start_data_stream())  # Lägg till korutinen på den aktiva loopen
    except RuntimeError:  # Om ingen loop är igång, skapa en ny loop
        loop = asyncio.new_event_loop()  # Skapa en ny event loop
        asyncio.set_event_loop(loop)  # Sätt den som aktiv
        loop.run_until_complete(start_data_stream())  # Kör korutinen
if __name__ == "__main__":
    main()
