from alpaca.trading.client import TradingClient
from alpaca.trading.stream import TradingStream
from config import API_KEY, SECRET_KEY
from config import PAPER
import asyncio

trading_client = TradingClient(API_KEY, SECRET_KEY, paper=PAPER)
trading_stream = TradingStream(API_KEY, SECRET_KEY, paper=PAPER)

async def get_account_info():
    account_info = trading_client.get_account()
    return {
        "buying_capacity": account_info.non_marginable_buying_power,
        "portfolio_value": account_info.portfolio_value,
        "pattern_day_trader": account_info.pattern_day_trader,
        "trading_blocked": account_info.trading_blocked
    }

async def place_buy_order(symbol: str, quantity: int, stock_price: float):
    limit_price = stock_price * 1.001 
    try:
        order = trading_client.limit_order_request(
            symbol=symbol,
            qty=quantity,
            side='buy',
            type='market',
            time_in_force='ioc',  # Immediate partial fill or cancel
            limit_price=limit_price
        )
        print(f"[BUY ORDER PLACED] {symbol} - Number of stocks: {quantity}")
        print(order)
    except Exception as e:
        print(f"[ERROR] Failed to place order for {symbol}: {e}")
        return None
    
async def place_sell_order(symbol: str, quantity: int):
    try:
        order = trading_client.market_order(
            symbol=symbol,
            qty=quantity,
            side='sell',
            type='market',
        )
        print(f"[SELL ORDER PLACED] {symbol} - Number of stocks: {quantity}")
        print(order)
    except Exception as e:
        print(f"[ERROR] Failed to place order for {symbol}: {e}")
        return None
    
async def handle_trade_update(trade_update):
    print(f"[TRADE UPDATE] - {trade_update}")
    
async def start_trading_stream():
    print("Starting trading stream...")
    trading_stream.subscribe_trade_updates(handle_trade_update)
    await trading_stream._run_forever()