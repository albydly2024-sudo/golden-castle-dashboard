print("BACKTESTER STARTING")
import ccxt
import pandas as pd
import time
from loguru import logger
from config import config

class Backtester:
    def __init__(self, exchange_id='binance'):
        self.exchange = getattr(ccxt, exchange_id)()
        
    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def run_backtest(self, symbol, timeframe='1h', days=30):
        """Run backtest for a specific symbol."""
        logger.info(f"Backtesting {symbol} on {timeframe} for last {days} days...")
        
        # Fetch data
        since = self.exchange.milliseconds() - days * 24 * 60 * 60 * 1000
        all_bars = []
        while since < self.exchange.milliseconds():
            bars = self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, since=since, limit=1000)
            if not bars: break
            all_bars += bars
            since = bars[-1][0] + 1
            time.sleep(self.exchange.rateLimit / 1000)

        df = pd.DataFrame(all_bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
        df['RSI'] = self.calculate_rsi(df['close'])
        
        # Simulation
        balance = 1000 # Start with $1000
        position = 0
        trades = 0
        
        for i in range(1, len(df)):
            rsi = df['RSI'].iloc[i]
            price = df['close'].iloc[i]
            
            # Buy Logic
            if rsi < 30 and position == 0:
                position = balance / price
                balance = 0
                trades += 1
            
            # Sell Logic
            elif rsi > 70 and position > 0:
                balance = position * price
                position = 0
                trades += 1
                
        # Final Balance
        final_val = balance if position == 0 else position * df['close'].iloc[-1]
        profit = ((final_val - 1000) / 1000) * 100
        
        return {
            'symbol': symbol,
            'initial': 1000,
            'final': final_val,
            'profit_pct': profit,
            'trades': trades
        }

if __name__ == "__main__":
    tester = Backtester()
    symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT']
    results = []
    
    print("\n--- BACKTESTING RESULTS (Last 30 Days) ---")
    for s in symbols:
        res = tester.run_backtest(s)
        results.append(res)
        print(f"{res['symbol']}: Profit: {res['profit_pct']:.2f}% | Trades: {res['trades']}")
