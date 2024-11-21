import base64
import datetime
import json
import os
import uuid
import requests
from nacl.signing import SigningKey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class DogeTrader:
    def __init__(self):
        """Initialize DOGE trader with API credentials from environment variables."""
        self.api_key = os.getenv('RH_API_KEY')
        private_key = os.getenv('RH_PRIVATE_KEY')
        
        if not self.api_key or not private_key:
            raise ValueError("Missing API credentials in environment variables.")
            
        private_key_seed = base64.b64decode(private_key)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"
        self.symbol = "DOGE-USD"

    def _get_current_timestamp(self) -> int:
        return int(datetime.datetime.now(tz=datetime.timezone.utc).timestamp())
        
    def _make_api_request(self, method: str, path: str, body: str = ""):
        timestamp = self._get_current_timestamp()
        headers = self._get_authorization_header(method, path, body, timestamp)
        url = self.base_url + path
        
        try:
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

    def _get_authorization_header(self, method: str, path: str, body: str, timestamp: int):
        message_to_sign = f"{self.api_key}{timestamp}{path}{method}{body}"
        signed = self.private_key.sign(message_to_sign.encode("utf-8"))
        
        return {
            "x-api-key": self.api_key,
            "x-signature": base64.b64encode(signed.signature).decode("utf-8"),
            "x-timestamp": str(timestamp)
        }

    def get_doge_price(self):
        """Get current DOGE price."""
        path = f"/api/v1/crypto/marketdata/best_bid_ask/?symbol={self.symbol}"
        result = self._make_api_request("GET", path)
        
        if result and 'results' in result:
            return {
                'bid': float(result['results'][0]['bid_price']),  # Price you can sell at
                'ask': float(result['results'][0]['ask_price']),  # Price you can buy at
                'timestamp': datetime.datetime.now().isoformat()
            }
        return None

    def get_doge_holdings(self):
        """Get current DOGE holdings."""
        path = "/api/v1/crypto/trading/holdings/?asset_code=DOGE"
        result = self._make_api_request("GET", path)
        
        if result and 'results' in result:
            return {
                'quantity': float(result['results'][0].get('quantity', 0)),
                'held_for_orders': float(result['results'][0].get('held_for_orders', 0))
            }
        return {'quantity': 0, 'held_for_orders': 0}

    def get_buying_power(self):
        """Get available buying power."""
        path = "/api/v1/crypto/trading/accounts/"
        result = self._make_api_request("GET", path)
        
        if result and 'buying_power' in result:
            return float(result['buying_power'])
        return 0.0

    def get_doge_orders(self, start_date=None):
        """Get DOGE order history."""
        filters = {'symbol': self.symbol}
        
        if start_date:
            filters['created_at_start'] = start_date.isoformat() + 'Z'
            
        path = "/api/v1/crypto/trading/orders/?"
        path += "&".join([f"{k}={v}" for k, v in filters.items()])
        return self._make_api_request("GET", path)

    def buy_doge(self, quantity: float):
        """
        Buy DOGE at market price
        Args:
            quantity: Amount of DOGE to buy
        """
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

    def sell_doge(self, quantity: float):
        """
        Sell DOGE at market price
        Args:
            quantity: Amount of DOGE to sell
        """
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

if __name__ == "__main__":
    # Initialize trader
    trader = DogeTrader()
    
    # Get current price
    price = trader.get_doge_price()
    if price:
        print(f"\nCurrent DOGE Prices:")
        print(f"Buy at: ${price['ask']}")
        print(f"Sell at: ${price['bid']}")
    
    # Get holdings
    holdings = trader.get_doge_holdings()
    print(f"\nDOGE Holdings: {holdings['quantity']}")
    
    # Get buying power
    buying_power = trader.get_buying_power()
    print(f"Available Buying Power: ${buying_power}")
    
    # Get today's orders
    today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
    orders = trader.get_doge_orders(today)
    if orders and 'results' in orders:
        print("\nToday's Orders:")
        for order in orders['results']:
            print(f"Type: {order['side']}, Amount: {order['filled_asset_quantity']}, "
                  f"Price: ${order.get('average_price', 'pending')}")