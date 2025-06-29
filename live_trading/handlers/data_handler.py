from handlers.trade_handler import make_trade_decision
from data.buffer import buffer
import pandas as pd
import traceback
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
            print("Stack trace:")
            traceback.print_exc()
        finally:
            bar_queue.task_done()

async def process_bar(bar):
    buffer.add(bar.symbol, bar)
    timestamp = pd.Timestamp(bar.timestamp)
    if bar.symbol == "SPY":
        await process_pending_bars(timestamp)
    else:
        df_sp = buffer.get_df("SPY")
        if timestamp in df_sp['timestamp'].values:
             await process_stock_data(bar.symbol)
        else:
            buffer.add_pending_bar(timestamp, bar.symbol)

async def process_pending_bars(timestamp):
    pending_bars = buffer.get_pending_bars(timestamp)
    if timestamp in pending_bars:
        symbols_to_process = pending_bars[timestamp]        
        for symbol in symbols_to_process:
            await process_stock_data(symbol)
    await buffer.empty_pending_bars()

async def process_stock_data(symbol):
    df = buffer.get_df(symbol)
    df_sp = buffer.get_df("SPY")  # This is the S&P 500 ETF used for creating features
    await make_trade_decision(df, df_sp)