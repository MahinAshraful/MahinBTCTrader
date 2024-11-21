import base64
import datetime
import json
import os
import uuid
from typing import Any, Dict, Optional, List
import requests
from nacl.signing import SigningKey
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class RobinhoodCryptoTrader:
    def __init__(self, symbol: str = "DOGE-USD"):
        """Initialize the crypto trader with API credentials from environment variables."""
        self.api_key = os.getenv('RH_API_KEY')
        private_key = os.getenv('RH_PRIVATE_KEY')
        
        if not self.api_key or not private_key:
            raise ValueError("Missing API credentials in environment variables. "
                           "Please ensure RH_API_KEY and RH_PRIVATE_KEY are set.")
            
        private_key_seed = base64.b64decode(private_key)
        self.private_key = SigningKey(private_key_seed)
        self.base_url = "https://trading.robinhood.com"
        self.symbol = symbol

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

    # Account Endpoints
    def get_account_info(self) -> Dict:
        """Get account information including buying power."""
        path = "/api/v1/crypto/trading/accounts/"
        return self._make_api_request("GET", path)

    # Market Data Endpoints
    def get_best_bid_ask(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Fetch best bid and ask prices for specified symbols.
        If no symbols provided, uses the default symbol.
        """
        if symbols is None:
            symbols = [self.symbol]
        
        symbol_params = "&".join([f"symbol={s}" for s in symbols])
        path = f"/api/v1/crypto/marketdata/best_bid_ask/?{symbol_params}"
        return self._make_api_request("GET", path)

    def get_estimated_price(self, side: str, quantity: str, symbol: Optional[str] = None) -> Dict:
        """
        Get estimated price for a potential trade.
        Args:
            side: 'bid', 'ask', or 'both'
            quantity: Comma-separated quantities (e.g., "0.1,1,1.999")
            symbol: Optional trading pair (defaults to self.symbol)
        """
        symbol = symbol or self.symbol
        path = f"/api/v1/crypto/marketdata/estimated_price/?symbol={symbol}&side={side}&quantity={quantity}"
        return self._make_api_request("GET", path)

    # Trading Pair Information
    def get_trading_pairs(self, symbols: Optional[List[str]] = None) -> Dict:
        """
        Get information about available trading pairs.
        If symbols provided, returns info for specific pairs.
        """
        path = "/api/v1/crypto/trading/trading_pairs/"
        if symbols:
            symbol_params = "&".join([f"symbol={s}" for s in symbols])
            path += f"?{symbol_params}"
        return self._make_api_request("GET", path)

    # Holdings Information
    def get_holdings(self, asset_codes: Optional[List[str]] = None) -> Dict:
        """
        Get current holdings information.
        If asset_codes provided, returns holdings for specific assets.
        """
        path = "/api/v1/crypto/trading/holdings/"
        if asset_codes:
            asset_params = "&".join([f"asset_code={code}" for code in asset_codes])
            path += f"?{asset_params}"
        return self._make_api_request("GET", path)

    # Order Management
    def get_orders(self, filters: Optional[Dict] = None) -> Dict:
        """
        Get list of orders with optional filters.
        Available filters:
        - created_at_start: ISO 8601 format
        - created_at_end: ISO 8601 format
        - updated_at_start: ISO 8601 format
        - updated_at_end: ISO 8601 format
        - symbol: trading pair
        - side: 'buy' or 'sell'
        - state: 'open', 'canceled', 'partially_filled', 'filled', 'failed'
        - type: 'limit', 'market', 'stop_limit', 'stop_loss'
        """
        path = "/api/v1/crypto/trading/orders/"
        if filters:
            filter_params = "&".join([f"{k}={v}" for k, v in filters.items()])
            path += f"?{filter_params}"
        return self._make_api_request("GET", path)

    def get_order(self, order_id: str) -> Dict:
        """Get details of a specific order."""
        path = f"/api/v1/crypto/trading/orders/{order_id}/"
        return self._make_api_request("GET", path)

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an open order."""
        path = f"/api/v1/crypto/trading/orders/{order_id}/cancel/"
        return self._make_api_request("POST", path)

    # Market Orders
    def place_market_buy(self, quantity: float, symbol: Optional[str] = None) -> Dict:
        """Place a market buy order."""
        return self._place_order("buy", "market", {"asset_quantity": str(quantity)}, symbol)

    def place_market_sell(self, quantity: float, symbol: Optional[str] = None) -> Dict:
        """Place a market sell order."""
        return self._place_order("sell", "market", {"asset_quantity": str(quantity)}, symbol)

    # Limit Orders
    def place_limit_buy(self, quantity: float, limit_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a limit buy order."""
        config = {
            "asset_quantity": str(quantity),
            "limit_price": str(limit_price),
            "time_in_force": "gtc"
        }
        return self._place_order("buy", "limit", config, symbol)

    def place_limit_sell(self, quantity: float, limit_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a limit sell order."""
        config = {
            "asset_quantity": str(quantity),
            "limit_price": str(limit_price),
            "time_in_force": "gtc"
        }
        return self._place_order("sell", "limit", config, symbol)

    # Stop Loss Orders
    def place_stop_loss_buy(self, quantity: float, stop_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a stop loss buy order."""
        config = {
            "asset_quantity": str(quantity),
            "stop_price": str(stop_price),
            "time_in_force": "gtc"
        }
        return self._place_order("buy", "stop_loss", config, symbol)

    def place_stop_loss_sell(self, quantity: float, stop_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a stop loss sell order."""
        config = {
            "asset_quantity": str(quantity),
            "stop_price": str(stop_price),
            "time_in_force": "gtc"
        }
        return self._place_order("sell", "stop_loss", config, symbol)

    # Stop Limit Orders
    def place_stop_limit_buy(self, quantity: float, stop_price: float, limit_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a stop limit buy order."""
        config = {
            "asset_quantity": str(quantity),
            "stop_price": str(stop_price),
            "limit_price": str(limit_price),
            "time_in_force": "gtc"
        }
        return self._place_order("buy", "stop_limit", config, symbol)

    def place_stop_limit_sell(self, quantity: float, stop_price: float, limit_price: float, symbol: Optional[str] = None) -> Dict:
        """Place a stop limit sell order."""
        config = {
            "asset_quantity": str(quantity),
            "stop_price": str(stop_price),
            "limit_price": str(limit_price),
            "time_in_force": "gtc"
        }
        return self._place_order("sell", "stop_limit", config, symbol)

    def _place_order(self, side: str, order_type: str, order_config: Dict, symbol: Optional[str] = None) -> Dict:
        """Internal method to place any type of order."""
        path = "/api/v1/crypto/trading/orders/"
        symbol = symbol or self.symbol
        
        body = {
            "client_order_id": str(uuid.uuid4()),
            "side": side,
            "type": order_type,
            "symbol": symbol,
            f"{order_type}_order_config": order_config
        }
        return self._make_api_request("POST", path, json.dumps(body))

def test_all_functions():
    """Test function to demonstrate all available functionality."""
    try:
        trader = RobinhoodCryptoTrader()
        
        # Test account info
        print("\n1. Testing Account Info:")
        print(json.dumps(trader.get_account_info(), indent=2))
        
        # Test market data
        print("\n2. Testing Best Bid/Ask:")
        print(json.dumps(trader.get_best_bid_ask(['BTC-USD', 'ETH-USD']), indent=2))
        
        print("\n3. Testing Estimated Price:")
        print(json.dumps(trader.get_estimated_price('ask', '0.1,1.0'), indent=2))
        
        # Test trading pairs
        print("\n4. Testing Trading Pairs:")
        print(json.dumps(trader.get_trading_pairs(['BTC-USD']), indent=2))
        
        # Test holdings
        print("\n5. Testing Holdings:")
        print(json.dumps(trader.get_holdings(['BTC', 'DOGE']), indent=2))
        
        # Test order listing
        print("\n6. Testing Order List:")
        filters = {
            'symbol': 'DOGE-USD',
            'state': 'filled'
        }
        print(json.dumps(trader.get_orders(filters), indent=2))
        
    except Exception as e:
        print(f"Error during testing: {e}")

if __name__ == "__main__":
    test_all_functions()