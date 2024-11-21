import base64
import datetime
import json
import os
import uuid
from typing import Any, Dict, Optional
import requests
from nacl.signing import SigningKey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DogeTrader:
    def __init__(self):
        """Initialize the DOGE trader with API credentials from environment variables."""
        self.api_key = os.getenv('RH_API_KEY')
        private_key = os.getenv('RH_PRIVATE_KEY')
        
        if not self.api_key or not private_key:
            raise ValueError("Missing API credentials in environment variables. "
                           "Please ensure RH_API_KEY and RH_PRIVATE_KEY are set.")
            
        private_key_seed = base64.b64decode(private_key)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"
        self.symbol = "DOGE-USD"
        
    def _get_current_timestamp(self) -> int:
        """Get current UTC timestamp."""
        return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        
    def _make_api_request(self, method: str, path: str, body: str = "") -> Any:
        """Make an authenticated API request."""
        timestamp = self._get_current_timestamp()
        headers = self._get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path
        
        try:
            response = {}
            if method == "GET":
                response = requests.get(url, headers=headers, timeout=10)
            elif method == "POST":
                response = requests.post(url, headers=headers, json=json.loads(body) if body else None, timeout=10)
            
            if response.status_code not in [200, 201]:
                print(f"Error: {response.status_code}")
                print(response.text)
                return None
                
            return response.json()
        except requests.RequestException as e:
            print(f"Error making API request: {e}")
            return None

    def _get_authorization_header(self, method: str, path: str, body: str, timestamp: int) -> Dict[str, str]:
        """Generate authorization headers."""
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message_to_sign.encode("utf-8"))
        
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp)
        }

    def get_account_info(self) -> Dict:
        """Get account information including buying power."""
        path = "/api/v1/crypto/trading/accounts/"
        return self._make_api_request("GET", path)

    def get_doge_price(self) -> Dict:
        """Get current DOGE price."""
        path = f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={self.symbol}"
        response = self._make_api_request("GET", path)
        if response and 'results' in response:
            return {
                'bid': response['results'][0]['bid_price'],
                'ask': response['results'][0]['ask_price'],
                'timestamp': datetime.datetime.now().isoformat()
            }
        return None

    def get_doge_holdings(self) -> Dict:
        """Get current DOGE holdings."""
        path = "/api/v1/crypto/trading/holdings/?asset_code=DOGE"
        return self._make_api_request("GET", path)

    def place_market_buy(self, quantity: float) -> Dict:
        """Place a market buy order for DOGE."""
        path = "/api/v1/crypto/trading/orders/"
        body = {
            "client_order_id": str(uuid.uuid4()),
            "side": "buy",
            "symbol": self.symbol,
            "type": "market",
            "market_order_config": {
                "asset_quantity": str(quantity)
            }
        }
        return self._make_api_request("POST", path, json.dumps(body))

    def place_market_sell(self, quantity: float) -> Dict:
        """Place a market sell order for DOGE."""
        path = "/api/v1/crypto/trading/orders/"
        body = {
            "client_order_id": str(uuid.uuid4()),
            "side": "sell",
            "symbol": self.symbol,
            "type": "market",
            "market_order_config": {
                "asset_quantity": str(quantity)
            }
        }
        return self._make_api_request("POST", path, json.dumps(body))

    def get_order_status(self, order_id: str) -> Dict:
        """Get the status of a specific order."""
        path = f"/api/v1/crypto/trading/orders/{order_id}/"
        return self._make_api_request("GET", path)

def test_trading_bot():
    """Test function to demonstrate usage of the DogeTrader class."""
    try:
        # Initialize trader using environment variables
        trader = DogeTrader()
        
        # Test 1: Get account info
        print("\nTesting account info:")
        account_info = trader.get_account_info()
        print(f"Account Info: {json.dumps(account_info, indent=2)}")
        
        # Test 2: Get DOGE price
        print("\nTesting DOGE price:")
        doge_price = trader.get_doge_price()
        print(f"DOGE Price: {json.dumps(doge_price, indent=2)}")
        
        # Test 3: Get holdings
        print("\nTesting DOGE holdings:")
        holdings = trader.get_doge_holdings()
        print(f"Holdings: {json.dumps(holdings, indent=2)}")
        
        # Example of trading functionality (commented out for safety)
        """
        # Buy DOGE
        buy_order = trader.place_market_buy(1.0)  # Buy 1 DOGE
        print(f"Buy Order: {json.dumps(buy_order, indent=2)}")
        
        # Check order status
        if buy_order and 'id' in buy_order:
            order_status = trader.get_order_status(buy_order['id'])
            print(f"Order Status: {json.dumps(order_status, indent=2)}")
        """
        
    except ValueError as e:
        print(f"Error: {e}")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    test_trading_bot()