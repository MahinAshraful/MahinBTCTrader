import base64
import datetime
import json
import os
import uuid
from nacl.signing import SigningKey
import requests
from dotenv import load_dotenv

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
            bid_price = result['results'][0].get('bid_price', 'N/A')
            ask_price = result['results'][0].get('ask_price', 'N/A')
            print(f"\nDOGE Price:")
            print(f"Buy Price: ${ask_price}")
            print(f"Sell Price: ${bid_price}")
        
        return result

    def get_holdings(self):
        """Get DOGE holdings."""
        path = "/api/v1/crypto/trading/holdings/?asset_code=DOGE"
        response = requests.get(
            self.base_url + path,
            headers=self._get_headers("GET", path),
            timeout=10
        )
        return response.json()

    def buy_doge(self, quantity: float):
        """Buy DOGE."""
        path = "/api/v1/crypto/trading/orders/"
        body = json.dumps({
            "client_order_id": str(uuid.uuid4()),
            "symbol": self.symbol,
            "side": "buy",
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
        return response.json()

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