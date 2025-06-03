import xgboost as xgb
from pathlib import Path

class Model:
    def __init__(self):
        current_dir = Path(__file__).parent
        model_path = current_dir / "trading_model_2.model"
        if not model_path.exists():
            raise FileNotFoundError(f"Model file not found at {model_path}")
        try:
            self.model = xgb.Booster()
            self.model.load_model(str(model_path))
        except Exception as e:
            print(f"[ERROR] Failed to load model: {e}")
            raise
    
    def predict(self, data):
        return self.model.predict(data)

model = Model()