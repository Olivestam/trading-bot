from handlers.trade_handler import make_trade_decision
from data.buffer import buffer  
import asyncio

bar_queue = asyncio.Queue()

async def handle_new_bar(bar):
    await bar_queue.put(bar)

async def process_bars():
    while True:
        bar = await bar_queue.get()
        try:
            await process_bar(bar)
        except Exception as e:
            print(f"[ERROR] Failed to process bar: {e}")
        finally:
            bar_queue.task_done()

async def process_bar(bar):
    buffer.add(bar.symbol, bar)
    df = buffer.get_df(bar.symbol)
    df_sp = buffer.get_df("SPY")  # This is the S&P 500 ETF used for creating features
    make_trade_decision(df, df_sp)
