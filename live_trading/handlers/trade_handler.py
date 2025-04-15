from features.feature_engineering import feature_engineering
from services.model_service import make_prediction
import pandas as pd

def make_trade_decision(df: pd.DataFrame, df_sp: pd.DataFrame):
    if len(df) < 20 or len(df_sp) < 20:
        print(f"[ERROR] Not enough data to make a decision. Length of df: {len(df)}, Length of df_sp: {len(df_sp)}")
        return
    
    features = feature_engineering(df, df_sp)
    print(features.head())
    """ prediction = make_prediction(features)

    decision = interpret_prediction(prediction)

    if decision != "hold":
        last_price = df.iloc[-1]["close"]
        execute_trade(symbol=df.iloc[-1]["symbol"], action=decision, price=last_price)
        print(f"[TRADE] {decision.upper()} {df.iloc[-1]['symbol']} at {last_price}")
    else:
        print(f"[HOLD] No action taken for {df.iloc[-1]['symbol']}") """