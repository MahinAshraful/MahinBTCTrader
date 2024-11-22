from tradingview_ta import TA_Handler

def get_crypto_supertrend(symbol, exchange="BINANCE", screener="crypto", interval="1m"):
    """
    Get Supertrend signal for crypto
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
        
        print(f"\n{symbol} Analysis:")
        print(f"Supertrend: {'UPTREND 🟢' if is_uptrend else 'DOWNTREND 🔴'}")
        print(f"Current Price: ${current_price:.6f}")
        print(f"SMA10: ${sma_10:.6f}")
        print(f"Overall Signal: {analysis.summary['RECOMMENDATION']}")
        
    except Exception as e:
        print(f"Error getting data for {symbol}: {str(e)}")

# Check DOGE
get_crypto_supertrend("DOGEUSDT")