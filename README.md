# Robinhood DOGE Trader Bot 🚀

A simple Python bot for trading DOGE on Robinhood using their Crypto API. This bot allows you to check DOGE prices, buy DOGE with USD, and sell your entire DOGE holdings with simple commands.

## Setup 🔧

1. Clone the repository:
```bash
git clone https://github.com/yourusername/robinhood-doge-trader.git
cd robinhood-doge-trader
```

2. Install required packages:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the root directory with your Robinhood API credentials:
```env
RH_API_KEY=your-api-key-here
RH_PRIVATE_KEY=your-private-key-here
```

> 🔒 **Security Note**: Never share or commit your `.env` file! Make sure it's in your `.gitignore`.

## Project Structure 📁

```
robinhood-doge-trader/
├── trader.py         # Main trading class
├── maintradebot.py   # Example usage
├── testenv.py        # Environment testing
├── requirements.txt  # Dependencies
├── .env             # API credentials (create this)
└── README.md        # This file
```

## Features ✨

### `trader.py`
Contains the `DogeTrader` class with the following methods:

- `get_price()`: Get current DOGE price
  ```python
  trader = DogeTrader()
  trader.get_price()  # Shows current DOGE price
  ```

- `buy_doge(dollars)`: Buy DOGE with USD
  ```python
  trader.buy_doge(10)  # Buy $10 worth of DOGE
  ```

- `sell_doge()`: Sell all DOGE holdings
  ```python
  trader.sell_doge()  # Sells entire DOGE balance
  ```

- `get_holdings()`: Check current DOGE holdings
  ```python
  trader.get_holdings()  # Shows your DOGE balance
  ```

### `testenv.py`
Verify your API credentials are properly set up:
```python
python testenv.py
```

### `maintradebot.py`
Example usage of the trading functions:
```python
from trader import DogeTrader

trader = DogeTrader()
trader.get_price()      # Check price
# trader.buy_doge(10)   # Buy $10 of DOGE
# trader.sell_doge()    # Sell all DOGE
```

## Fees 💰
- Trading fee: 0.45% per transaction (built into the spread)
- Applies to both buying and selling
- Example: $10 trade = ~$0.045 fee

## Requirements 📋
See [requirements.txt](requirements.txt) for full list:
- python-dotenv
- requests
- PyNaCl

## Security 🔐
- Store API credentials in `.env` file
- Never share your private key
- Add `.env` to `.gitignore`

## Disclaimer ⚠️
This bot is for educational purposes. Use at your own risk. Cryptocurrency trading carries significant risks.

## License 📄
MIT License