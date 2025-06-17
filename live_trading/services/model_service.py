import xgboost as xgb
import numpy as np
from data.model import model

def make_prediction(features):
    X = features.drop(columns=["target", "symbol", "timestamp", "future_close"])
    data = xgb.DMatrix(X)
    pred_prob = model.predict(data)
    X["prediction"] = np.argmax(pred_prob, axis=1)
    X["confidence"] = np.max(pred_prob, axis=1)
    X['prediction'] = X['prediction'].round().astype(int)

    return {
        'symbol': features['symbol'].iloc[0],
        'timestamp': features['timestamp'].iloc[0],
        'prediction': int(X['prediction'].iloc[0]),
        'confidence': float(X['confidence'].iloc[0])
    }

