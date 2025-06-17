from collections import defaultdict
from datetime import datetime
from services.trading_service import get_account_info
import asyncio

"""
BuyTracker
- This class is used to track the number of buy orders for each stock on the current day and the current buying capacity.
- This is needed make sure we trade the same stock less then 4 times a day to avoid being flagged as a pattern day trader.
- We also need to make sure we have enough buying capacity to buy the stock and never want to buy more than 20% of the total portfolio value.
- Thread-safe for concurrent async access from multiple WebSocket streams.
"""
class BuyTracker:
    def __init__(self):
        self.buy_counts = defaultdict(int)
        self.buying_capacity = 0
        self.total_portfolio_value = 0
        self.current_date = None
        self.stocks_owned = defaultdict(int)
        self._lock = asyncio.Lock()

    async def record_buy(self, symbol: str, quantity: int):
        async with self._lock:
            self.buy_counts[symbol] += 1
            self.stocks_owned[symbol] += quantity

    async def record_sell(self, symbol: str, quantity: int, price: float):
        async with self._lock:
            self.stocks_owned[symbol] -= quantity
            self.buying_capacity += quantity * price

    async def record_placed_order(self, amount: float):
        # Lock money in placed order
        async with self._lock:
            self.buying_capacity -= amount

    async def get_buying_capacity(self):
        async with self._lock:
            return self.buying_capacity
    
    async def get_stocks_owned(self, symbol: str):
        async with self._lock:
            return self.stocks_owned[symbol]
    
    async def possible_buy(self, symbol: str):
        async with self._lock:
            await self.check_new_day(datetime.now())
            # Check if we have enough buying capacity and if we haven't bought this stock more than 3 times today.
            # We put 0.201 here since we can buy for maximum 0.1 % above price at decision time.
            return self.buying_capacity > (self.total_portfolio_value * 0.201) and self.buy_counts[symbol] < 3

    async def new_day_reset(self):
        account_info = await get_account_info()
        async with self._lock:
            self.buy_counts = defaultdict(int)
            self.buying_capacity = account_info['buying_capacity']
            self.total_portfolio_value = account_info['portfolio_value']

    async def check_new_day(self, timestamp: datetime):
        current_day = timestamp.date()
        should_reset = False
        
        async with self._lock:
            should_reset = self.current_date != current_day
            
        if should_reset:
            await self.new_day_reset()
            async with self._lock:
                self.current_date = current_day

# Create a singleton instance
buy_tracker = BuyTracker()