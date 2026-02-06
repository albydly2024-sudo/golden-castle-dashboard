import time
import config
from market_data import BinanceClient
from strategy import Strategy
import database
import telegram_bot
import sys

def main():
    print("Starting Professional Binance Bot (Phase 3)...")
    print("Dashboard & Telegram Integration Active")
    
    # Initialize DB
    database.init_db()
    
    # Initialize Client and Strategy
    client = BinanceClient()
    strategy = Strategy()
    
    try:
        while True:
            # Get current timestamp
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            print(f"\n[{now}] Scanning Market...")
            
            for symbol in config.TARGET_PAIRS:
                # 1. Fetch Data (1h and 4h for MTF)
                df = client.fetch_data(symbol, config.TIMEFRAME, config.LIMIT)
                df_4h = client.fetch_data(symbol, '4h', 100) # Fetch 4h trend
                
                if df is not None and not df.empty and len(df) > 200:
                    # 2. Analyze
                    df = strategy.apply_indicators(df)
                    signal, setup = strategy.check_signal(df, df_mtf=df_4h)
                    
                    # 3. Output & Log Status
                    latest_price = df.iloc[-1]['close']
                    ema_200 = df.iloc[-1]['EMA_200']
                    rsi = df.iloc[-1]['RSI']
                    trend = "UP" if latest_price > ema_200 else "DOWN"
                    
                    # Log to DB (For Dashboard)
                    database.update_market_status(symbol, latest_price, trend, rsi)
                    
                    print(f"{symbol:<12} | {latest_price:<10.2f} | {trend:<10} | {signal:<10}")
                    
                    if signal in ["BUY", "SELL"] and setup:
                        emoji = "🚀" if signal == "BUY" else "📉"
                        print("\n" + "*"*40)
                        print(f"{emoji} {signal} SIGNAL: {symbol}")
                        print("*"*40 + "\n")
                        
                        # Log Signal to DB
                        database.log_signal(symbol, signal, setup['entry'], setup['stop_loss'], setup['take_profit'], setup['reason'])
                        
                        # Send Telegram Alert
                        telegram_bot.send_signal_alert(symbol, setup)

                else:
                    print(f"{symbol:<12} | Waiting for data...")

            print(f"\nWaiting 5s...")
            time.sleep(5) 

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
