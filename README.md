# Trading Bot

An automated trading system that uses machine learning to identify market opportunities and execute trades based on real-time data.

## Overview

This trading bot integrates with the Alpaca API to stream real-time market data, make predictions using a trained XGBoost model, and automatically execute trades based on those predictions. The system runs multiple concurrent websocket connections and uses asyncio to handle real-time events efficiently.

## Features

- Real-time market data streaming
- Concurrent processing of data and trading streams
- Machine learning-based prediction model
- Automated trade execution
- Pattern Day Trading (PDT) rule compliance
- Historical data analysis
- Thread-safe state management
- PostgreSQL database integration for trade tracking

## Architecture

The system is organized into several components:

- **Data Layer**: Handles data storage, buffering, and state management
- **Services**: Connects to external APIs and handles core functionality
- **Handlers**: Processes events and coordinates responses
- **Features**: Transforms raw data into model-ready features
- **Core**: Manages application lifecycle and configuration

## Requirements

- Python 3.9+
- PostgreSQL
- Alpaca account with API keys
- Required Python packages (see `requirements.txt`)

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/trading-bot.git
   cd trading-bot
   ```

2. Install dependencies:
   ```
   pip install -r requirements.txt
   ```

3. Set up the database:
   ```
   createdb trading_bot_db
   python -m live_trading.data.database
   ```

4. Create a `.env` file with your configuration:
   ```
   API_KEY=your_alpaca_api_key
   SECRET_KEY=your_alpaca_secret_key
   PAPER=True
   ENV=dev
   DB_HOST=localhost
   DB_NAME=trading_bot_db
   DB_USER=your_db_user
   DB_PASSWORD=your_db_password
   ```

## Usage

Start the trading bot:

```
python -m live_trading.main
```

The system will:
1. Load historical data (in dev mode)
2. Start two concurrent websocket streams for data and trading
3. Begin processing incoming market data
4. Make trading decisions based on the ML model predictions
5. Execute trades when confidence thresholds are met

## Configuration

Key configuration options in `config.py`:

- `PAPER`: Set to `True` for paper trading, `False` for live trading
- `ENV`: Set to `dev` for development mode (loads historical data), `prod` for production
- `SYMBOLS`: List of stock symbols to trade
- Confidence thresholds for buy/sell decisions

## Project Structure

```
live_trading/
│
├── data/                  # Data management
│   ├── buffer.py          # Market data buffer
│   ├── buy_tracker.py     # Trade tracking and limits
│   ├── database.py        # PostgreSQL interface
│   └── model.py           # ML model handler
│
├── services/              # External integrations
│   ├── stock_data_service.py  # Market data streaming
│   ├── trading_service.py     # Order execution
│   └── model_service.py       # ML prediction
│
├── handlers/              # Event processing
│   ├── data_handler.py    # Market data processing
│   └── trade_handler.py   # Trading decisions
│
├── features/              # Feature engineering
│   └── feature_engineering.py  # Feature creation pipeline
│
├── main.py                # Application entry point
└── config.py              # Configuration settings
```

## Concurrency Model

The system uses asyncio for concurrent processing:
- Multiple websockets operate concurrently within a single event loop
- Thread-safe state management using asyncio locks
- Producer-consumer pattern with queues for safe data handling

## Future Improvements

- Implement testing framework
- Add analysis for monitoring and control
- Enhance metrics and visualization
- Implement logging for easier error handling

## License

MIT License

## Disclaimer

This software is for educational purposes only. Trading involves risk of financial loss. The authors take no responsibility for financial decisions made using this software.
