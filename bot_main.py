import time
import config
from market_data import BinanceClient
from strategy import Strategy
import db_manager as database
import telegram_bot
from risk_manager import RiskManager
from trade_executor import TradeExecutor
import sys

def main():
    print("Starting Professional Binance Bot (Phase 3)...")
    print("Dashboard & Telegram Integration Active")
    
    # Initialize DB
    database.init_db()
    
    # Initialize Client and Strategy
    # Initialize Client, Strategy, and Risk/Executor
    client = BinanceClient()
    strategy = Strategy()
    risk_manager = RiskManager(initial_capital=config.TRADING_CAPITAL)
    executor = TradeExecutor(client)
    
    # Load Active Positions from DB
    executor.active_positions = database.get_active_positions()
    print(f"📂 Loaded {len(executor.active_positions)} active positions from database.")
    
    try:
        while True:
            # Get current timestamp
            now = time.strftime('%Y-%m-%d %H:%M:%S')
            current_prices = {}

            for symbol in config.TARGET_PAIRS:
                # 1. Fetch Data (1h and 4h for MTF)
                df = client.fetch_data(symbol, config.TIMEFRAME, config.LIMIT)
                df_4h = client.fetch_data(symbol, '4h', 100) # Fetch 4h trend
                
                if df is not None and not df.empty and len(df) > 200:
                    latest_price = df.iloc[-1]['close']
                    current_prices[symbol] = latest_price
                    
                    # 2. Analyze
                    df = strategy.apply_indicators(df)
                    signal, setup = strategy.check_signal(df, df_mtf=df_4h)
                    
                    # 3. Output & Log Status
                    ema_200 = df.iloc[-1]['EMA_200']
                    rsi = df.iloc[-1]['RSI']
                    trend = "UP" if latest_price > ema_200 else "DOWN"
                    
                    # Log to DB (For Dashboard)
                    database.update_market_status(symbol, latest_price, trend, rsi)
                    
                    print(f"{symbol:<12} | {latest_price:<10.2f} | {trend:<10} | {signal:<10}")
                    
                    # 4. Handle Trading Execution
                    if signal in ["BUY", "SELL"] and setup:
                        # Check if we already have a position
                        if symbol not in executor.active_positions:
                            # Risk Check
                            if risk_manager.can_open_position(len(executor.active_positions)):
                                # Calculate Position Size
                                size = risk_manager.calculate_position_size(setup['entry'], setup['stop_loss'])
                                
                                # Instead of auto-executing, log as PENDING
                                # emoji = "🚀" if signal == "BUY" else "📉"
                                # print(f"\n{emoji} {signal} ORDER EXECUTED: {symbol} at {setup['entry']}")
                                
                                # Log Signal as PENDING (Dashboard will handle approval)
                                database.log_signal(symbol, signal, setup['entry'], setup['stop_loss'], setup['take_profit'], setup['reason'])
                                telegram_bot.send_signal_alert(symbol, setup)
                                print(f"📝 {signal} Signal logged as PENDING for {symbol}. Awaiting dashboard approval.")

                else:
                    print(f"{symbol:<12} | Waiting for data...")

            # 5. Check for APPROVED signals in DB to execute
            approved_df = database.get_approved_signals()
            if not approved_df.empty:
                for _, row in approved_df.iterrows():
                    print(f"✅ Executing APPROVED signal for {row['symbol']}...")
                    
                    # Re-calculate size based on current capital
                    size = risk_manager.calculate_position_size(row['price'], row['stop_loss'])
                    
                    # Create a mock setup object for the executor
                    setup = {
                        'type': row['type'],
                        'entry': row['price'],
                        'stop_loss': row['stop_loss'],
                        'take_profit': row['take_profit']
                    }
                    
                    # Execute
                    position = executor.open_position(row['symbol'], setup, size)
                    
                    if position:
                        # Mark as EXECUTED
                        database.update_signal_status(row['id'], 'EXECUTED')
                        print(f"🚀 Trade executed and marked as EXECUTED in DB.")
                    else:
                        # Mark as FAILED (to prevent infinite loop)
                        database.update_signal_status(row['id'], 'FAILED')
                        print(f"❌ Trade failed to execute. Marked as FAILED.")
                    print(f"🚀 Trade executed and marked as EXECUTED in DB.")

            # 6. Check Active Positions (Trailing Stops)
            executor.check_trailing_stops(current_prices)

            print(f"\nWaiting 5s...")
            time.sleep(5) 

    except KeyboardInterrupt:
        print("\nBot stopped by user.")
        sys.exit(0)
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    main()
