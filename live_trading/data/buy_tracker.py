from collections import defaultdict
from datetime import datetime
from services.trading_service import get_account_info

""" 
BuyTracker
- This class is used to track the number of buy orders for each stock on the current day and the current buying capacity.
- This is needed make sure we trade the same stock less then 4 times a day to avoid being flagged as a pattern day trader.
- We also need to make sure we have enough buying capacity to buy the stock and never want to buy more than 20% of the total portfolio value.

"""
class BuyTracker:
    def __init__(self):
        self.buy_counts = defaultdict(int)
        self.buying_capacity = 0
        self.total_portfolio_value = 0
        self.current_date = None
        self.stocks_owned = defaultdict(int)

    def record_buy(self, symbol: str, quantity: int):
        self.buy_counts[symbol] += 1
        self.stocks_owned[symbol] += quantity

    def record_sell(self, symbol: str, quantity: int, price: float):
        self.stocks_owned[symbol] -= quantity
        self.buying_capacity += quantity * price

    def record_placed_order(self, amount: float):
        # Lock money in placed order
        self.buying_capacity -= amount

    def get_buying_capacity(self):
        return self.buying_capacity
    
    def get_stocks_owned(self, symbol: str):
        return self.stocks_owned[symbol]
    
    def possible_buy(self, symbol: str):
        self.check_new_day(datetime.now())
        # Check if we have enough buying capacity and if we haven't bought this stock more than 3 times today.
        # We put 0.201 here since we can buy for maximum 0.1 % above price at decision time.
        return self.buying_capacity > (self.total_portfolio_value * 0.201) and self.buy_counts[symbol] < 3

    def new_day_reset(self):
        account_info = get_account_info()
        self.buy_counts = defaultdict(int)
        self.buying_capacity = account_info['buying_capacity']
        self.total_portfolio_value = account_info['portfolio_value']

    def check_new_day(self, timestamp: datetime):
        current_day = timestamp.date()
        if self.current_date != current_day:
            self.new_day_reset()
            self.current_date = current_day

buy_tracker = BuyTracker()
