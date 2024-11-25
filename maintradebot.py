from trader import BTCTrader
import time
from datetime import datetime

def main():
    trader = BTCTrader()
    position = False
    
    print("Starting BTC trading bot...")
    print("Waiting for signals...")
    
    while True:
        try:
            current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            signal = trader.check_supertrend()
            
            if signal is None:
                print(f"[{current_time}] Error getting signal, waiting for next check...")
                time.sleep(20)
                continue
                
            if signal == "BUY" and not position:
                print(f"[{current_time}] 💰 Executing BUY order...")
                result = trader.buy_BTC(10)
                if result:
                    position = True
                    print(f"[{current_time}] ✅ BUY order executed")
                else:
                    print(f"[{current_time}] ❌ BUY order failed")
            elif signal == "SELL" and position:
                print(f"[{current_time}] 💰 Executing SELL order...")
                result = trader.sell_BTC()
                if result:
                    position = False
                    print(f"[{current_time}] ✅ SELL order executed")
                else:
                    print(f"[{current_time}] ❌ SELL order failed")
            
            time.sleep(20)
            
        except KeyboardInterrupt:
            print("\nBot stopped by user")
            if position:
                print("Closing position before exiting...")
                trader.sell_BTC()
            break
        except Exception as e:
            print(f"[{current_time}] Error: {e}")
            time.sleep(20)

if __name__ == "__main__":
    main()