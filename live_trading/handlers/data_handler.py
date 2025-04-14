from data.buffer import buffer  
from data.buy_tracker import buy_tracker
from datetime import datetime

async def handle_new_bar(bar):
    print(bar)
    print(type(bar))
