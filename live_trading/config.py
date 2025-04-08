from dotenv import load_dotenv
import os

load_dotenv()
API_KEY = os.getenv("ALPACA_API_KEY")
SECRET_KEY = os.getenv("ALPACA_SECRET_KEY")
ENV = os.getenv("ENV")
if ENV == "dev":
    PAPER = True
else:
    PAPER = False