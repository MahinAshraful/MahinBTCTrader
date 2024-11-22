import base64
import datetime
import json
import os
import uuid
from nacl.signing import SigningKey
import requests
from dotenv import load_dotenv
from tradingview_ta import TA_Handler

load_dotenv()

class DogeTrader:
    def __init__(self):
        self.api_key = os.getenv('RH_API_KEY')
        private_key = os.getenv('RH_PRIVATE_KEY')
        
        if not self.api_key or not private_key:
            raise ValueError("Missing API credentials in environment variables.")
            
        private_key_seed = base64.b64decode(private_key)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"
        self.symbol = "DOGE-USD"

    def _get_headers(self, method: str, path: str, body: str = ""):
        timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        message = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message.encode("utf-8"))
        
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp)
        }

    def get_price(self):
        """Get current DOGE price."""
        path = f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={self.symbol}"
        response = requests.get(
            self.base_url + path,
            headers=self._get_headers("GET", path),
            timeout=10
        )
        result = response.json()
        
        if result and 'results' in result and result['results']:
            price = float(result['results'][0]['price'])
            print(f"DOGE: ${price:.4f}")
            return price

    def get_holdings(self):
        """Get DOGE holdings."""
        path = "/api/v1/crypto/trading/holdings/?asset_code=DOGE"
        response = requests.get(
            self.base_url + path,
            headers=self._get_headers("GET", path),
            timeout=10
        )
        return response.json()

    def buy_doge(self, dollars: float):
        """Buy DOGE with USD."""
        # Get price
        price_data = requests.get(
            self.base_url + f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={self.symbol}",
            headers=self._get_headers("GET", f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={self.symbol}"),
            timeout=10
        ).json()
        
        # Calculate quantity
        quantity = round((dollars / float(price_data['results'][0]['price'])) * 100) / 100
        
        # Prepare order data
        order_data = {
            "client_order_id": str(uuid.uuid4()),
            "symbol": self.symbol,
            "side": "buy",
            "type": "market",
            "market_order_config": {
                "asset_quantity": f"{quantity:.2f}"
            }
        }
        
        # Place order
        body = json.dumps(order_data)
        response = requests.post(
            self.base_url + "/api/v1/crypto/trading/orders/",
            headers=self._get_headers("POST", "/api/v1/crypto/trading/orders/", body),
            json=order_data,
            timeout=10
        )
        
        try:
            if response.status_code == 201:
                print(f"Bought {quantity:.2f} DOGE")
                return response.json()
            else:
                print(f"Order failed: {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def sell_doge(self):
        """Sell all DOGE."""
        holdings = self.get_holdings()

        if holdings and 'results' in holdings and holdings['results']:
            quantity = holdings['results'][0].get('quantity_available_for_trading', '0')
            if float(quantity) > 0:
                path = "/api/v1/crypto/trading/orders/"
                body = json.dumps({
                    "client_order_id": str(uuid.uuid4()),
                    "symbol": self.symbol,
                    "side": "sell",
                    "type": "market",
                    "market_order_config": {
                        "asset_quantity": str(quantity)
                    }
                })
                response = requests.post(
                    self.base_url + path,
                    headers=self._get_headers("POST", path, body),
                    json=json.loads(body),
                    timeout=10
                )
                print("Sold all DOGE")
                return response.json()
            
    def get_supertrend(self, symbol="DOGEUSDT", exchange="BINANCE", screener="crypto", interval="5m"):
        """
        Get Supertrend signal for crypto using 5m candles
        """
        try:
            handler = TA_Handler(
                symbol=symbol,
                screener=screener,
                exchange=exchange,
                interval=interval
            )
            
            analysis = handler.get_analysis()
            
            # Get current price and indicators
            current_price = analysis.indicators['close']
            sma_10 = analysis.indicators['SMA10']
            
            # Check trend
            is_uptrend = current_price > sma_10 and analysis.summary['RECOMMENDATION'] in ['BUY', 'STRONG_BUY']
            
            print(f"\n{symbol} 5m Analysis:")
            print(f"Supertrend: {'UPTREND 🟢' if is_uptrend else 'DOWNTREND 🔴'}")
            print(f"Current Price: ${current_price:.6f}")
            print(f"SMA10: ${sma_10:.6f}")
            print(f"Overall Signal: {analysis.summary['RECOMMENDATION']}")
            return 'Buy' if is_uptrend else 'Sell'
            
        except Exception as e:
            print(f"Error getting data for {symbol}: {str(e)}")
            return None