from features.feature_engineering import feature_engineering
from services.model_service import make_prediction
from services.trading_service import place_buy_order, place_sell_order
from data.buy_tracker import buy_tracker
import pandas as pd

def make_trade_decision(df: pd.DataFrame, df_sp: pd.DataFrame):
    if len(df) < 20 or len(df_sp) < 20:
        print(f"[ERROR] Not enough data to make a decision. Length of df: {len(df)}, Length of df_sp: {len(df_sp)}")
        return
    
    features = feature_engineering(df, df_sp)
    prediction = make_prediction(features)

    symbol = df['symbol'].iloc[0]
    stock_price = df['close'].iloc[-1]
    if prediction['prediction'] == 1 and prediction['confidence'] > 0.75:
        # Buy signal
        if buy_tracker.possible_buy(symbol):
            buying_capacity = buy_tracker.get_buying_capacity()
            quantity = int(buying_capacity / stock_price)
            buy_tracker.record_placed_order(quantity*stock_price)
            place_buy_order(symbol, quantity, stock_price)
        else:
            print(f"[SKIP BUY] {symbol} - Not enough buying capacity or too many trades today.")
    elif prediction['prediction'] == 2:
        # Sell signal
        stocks_owned = buy_tracker.get_stocks_owned(symbol)
        if stocks_owned > 0:
            place_sell_order(symbol, stocks_owned)