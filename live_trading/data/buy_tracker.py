from collections import defaultdict
from datetime import datetime

""" 
BuyTracker
- This class is used to track the number of buy orders for each stock on the current day.
- This is needed make sure we trade the same stock less then 4 times a day to avoid being flagged as a pattern day trader.

"""
class BuyTracker:
    def __init__(self):
        self.buy_counts = defaultdict(int)
        self.current_date = None

    def record_buy(self, symbol: str):
        self.buy_counts[symbol] += 1

    def get_buy_count(self, symbol: str):
        return self.buy_counts[symbol]

    def reset_buy_counts(self):
        self.buy_counts = defaultdict(int)

    def check_new_day(self, timestamp: datetime):
        current_day = timestamp.date()
        if self.current_date != current_day:
            self.reset_buy_counts()
            self.current_date = current_day
