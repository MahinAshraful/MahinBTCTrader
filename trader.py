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

class BTCTrader:
    def __init__(self):
        self.api_key = os.getenv('RH_API_KEY')
        private_key = os.getenv('RH_PRIVATE_KEY')
        
        if not self.api_key or not private_key:
            raise ValueError("Missing API credentials in environment variables.")
            
        private_key_seed = base64.b64decode(private_key)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"
        self.symbol = "BTC-USD"

    def _get_headers(self, method: str, path: str, body: str = ""):
        timestamp = int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        message = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message.encode("utf-8"))
        
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp)
        }

    def get_holdings(self):
        """Get BTC holdings."""
        path = "/api/v1/crypto/trading/holdings/?asset_code=BTC"
        response = requests.get(
            self.base_url + path,
            headers=self._get_headers("GET", path),
            timeout=10
        )
        return response.json()
    
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



    def buy_BTC(self, dollars: float):
        """Buy BTC with USD."""
        # Get current price first
        current_price = self.get_price()
        if not current_price:
            print("Could not get current price")
            return None
            
        # Calculate quantity in BTC
        quantity = round(dollars / current_price, 6)  # Round to 6 decimal places
        
        # Check minimum order size (0.000001 BTC)
        if quantity < 0.000001:
            print(f"Order too small. Minimum order is 0.000001 BTC (${0.000001 * current_price:.2f})")
            return None

        # Prepare order data
        order_data = {
            "client_order_id": str(uuid.uuid4()),
            "symbol": self.symbol,
            "side": "buy",
            "type": "market",
            "market_order_config": {
                "asset_quantity": f"{quantity:.6f}"  # Format with 6 decimal places
            }
        }
        
        # Place order
        body = json.dumps(order_data)
        try:
            response = requests.post(
                self.base_url + "/api/v1/crypto/trading/orders/",
                headers=self._get_headers("POST", "/api/v1/crypto/trading/orders/", body),
                json=order_data,
                timeout=10
            )
            
            if response.status_code == 201:
                print(f"Bought {quantity:.6f} BTC at ~${current_price:.2f}")
                return response.json()
            else:
                print(f"Order failed: {response.text}")
                return None
        except Exception as e:
            print(f"Error: {e}")
            return None

    def sell_BTC(self):
        """Sell all BTC."""
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
                print("Sold all BTC")
                return response.json()
            
    def check_supertrend(self):
        """Check BTC Supertrend signal using TAAPI.IO API."""
        try:
            taapi_key = os.getenv('TAAPI_API_KEY')
            if not taapi_key:
                raise ValueError("Missing TAAPI API key in environment variables.")

            url = "https://api.taapi.io/supertrend"
            
            params = {
                'secret': taapi_key,
                'exchange': 'binance',
                'symbol': 'BTC/USDT',
                'interval': '5m',
                'period': 7,  
                'multiplier': 3  
            }

            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            current_price = self.get_price()

            if data['valueAdvice'] == 'long':
                print(f"BTC: ${current_price:.2f} | Signal: BUY (Supertrend: ${data['value']:.2f})")
                return "BUY"
            else:
                print(f"BTC: ${current_price:.2f} | Signal: SELL (Supertrend: ${data['value']:.2f})")
                return "SELL"

        except requests.RequestException as e:
            print(f"API request failed: {e}")
            return None
        except KeyError as e:
            print(f"Invalid API response format: {e}")
            return None
        except Exception as e:
            print(f"Error: {e}")
            return None
            
    