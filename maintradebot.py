import time
from trader import DogeTrader

def run_trading_bot():
    trader = DogeTrader()
    dollars_to_trade = 5 
    in_position = False
    waiting_for_sell = False
    
    print("Starting trading bot...")
    print("Waiting for initial setup...")
    time.sleep(5)  # Initial delay to let everything initialize

    while True:
        try:
            signal = trader.get_supertrend()  # Using default 5m timeframe
            
            if signal is None:
                print("Error getting signal, waiting 15 seconds...")
                time.sleep(15)
                continue

            # Check if we're waiting for first sell signal
            if not waiting_for_sell:
                if signal == 'Buy':
                    print("Found initial buy signal, waiting for sell before starting...")
                    waiting_for_sell = True
                else:
                    print("Waiting for first buy signal...")
            
            # Normal trading logic after initial setup
            elif not in_position and signal == 'Buy':
                print("\nBUY Signal Detected!")
                result = trader.buy_doge(dollars_to_trade)
                if result:
                    in_position = True
                    print(f"Successfully bought DOGE")
                
            elif in_position and signal == 'Sell':
                print("\nSELL Signal Detected!")
                result = trader.sell_doge()
                if result:
                    in_position = False
                    print(f"Successfully sold DOGE")
            
            else:
                if in_position:
                    print("\nHolding position...")
                else:
                    print("\nWaiting for buy signal...")
            
            # Wait before next check
            time.sleep(15)
            
        except KeyboardInterrupt:
            print("\nBot stopped by user!")
            if in_position:
                print("WARNING: Still holding position!")
            break
        except Exception as e:
            print(f"Error occurred: {e}")
            time.sleep(15)

if __name__ == "__main__":
    run_trading_bot()