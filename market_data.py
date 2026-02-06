import ccxt
import pandas as pd
import config
from datetime import datetime
import yfinance as yf

class BinanceClient:
    def __init__(self):
        # Check if keys are configured
        if config.SECRET_KEY == 'YOUR_SECRET_KEY_HERE':
            print("⚠️ secret Key excluded. Running in Public Mode (Analysis Only).")
            self.exchange = ccxt.binance({'enableRateLimit': True})
        else:
            self.exchange = ccxt.binance({
                'apiKey': config.API_KEY,
                'secret': config.SECRET_KEY,
                'enableRateLimit': True,
                'options': {'defaultType': 'spot'}
            })

    def fetch_data(self, symbol, timeframe, limit):
        """
        Fetches historical OHLCV data. 
        Supports Binance (Crypto) and Yahoo Finance (Gold).
        """
        # --- Yahoo Finance Logic (Gold) ---
        if symbol in ['GC=F', 'XAU-USD', 'GOLD']:
            try:
                # Map timeframe to yfinance format
                # yfinance supports: 1m, 2m, 5m, 15m, 30m, 60m, 90m, 1h, 1d, 5d, 1wk, 1mo, 3mo
                interval_map = {'1m': '1m', '5m': '5m', '15m': '15m', '1h': '1h', '4h': '1h', '1d': '1d'}
                yf_interval = interval_map.get(timeframe, '1h')
                
                # Fetch data
                # period='1mo' is enough for 300 candles of 1h. 
                # For 1m data, max is 7 days.
                period = '1mo'
                if timeframe == '1m': period = '5d'

                ticker = yf.Ticker(symbol)
                df = ticker.history(period=period, interval=yf_interval)
                
                if df.empty:
                    print(f"⚠️ Yahoo Finance returned no data for {symbol}")
                    return None

                # Normalize to match CCXT format
                df = df.reset_index()
                # Yahoo columns: Date/Datetime, Open, High, Low, Close, Volume, Dividends, Stock Splits
                # We need: timestamp, open, high, low, close, volume
                
                # Handling Timezone to matching UTC timestamp style (optional but good for consistency)
                # But mostly just need the column names
                df.rename(columns={
                    'Date': 'timestamp', 'Datetime': 'timestamp',
                    'Open': 'open', 'High': 'high', 'Low': 'low', 
                    'Close': 'close', 'Volume': 'volume'
                }, inplace=True)
                
                # Ensure columns exist and are lower case
                df = df[['timestamp', 'open', 'high', 'low', 'close', 'volume']]
                
                return df.tail(limit)

            except Exception as e:
                print(f"Error fetching Yahoo data for {symbol}: {e}")
                return None

        # --- Binance Logic (Crypto) ---
        try:
            # print(f"Fetching data for {symbol} ({timeframe})...") 
            ohlcv = self.exchange.fetch_ohlcv(symbol, timeframe, limit=limit)
            
            if not ohlcv:
                # print(f"No data returned for {symbol}")
                return None

            df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # Convert timestamp to readable date
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            
            return df
        
        except Exception as e:
            # print(f"Error fetching data for {symbol}: {e}")
            return None

    def get_current_price(self, symbol):
        try:
            ticker = self.exchange.fetch_ticker(symbol)
            return ticker['last']
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None

    def get_account_balance(self):
        """
        Fetches the total balance for USDT and PAXG (Gold).
        """
        try:
            # fetch_balance needs authentication
            balance = self.exchange.fetch_balance()
            
            # Extract specific balances
            usdt_total = balance.get('USDT', {}).get('total', 0)
            paxg_total = balance.get('PAXG', {}).get('total', 0)
            
            return {
                'USDT': round(usdt_total, 2),
                'PAXG': round(paxg_total, 4),
                'timestamp': datetime.now().strftime('%H:%M:%S')
            }
        except Exception as e:
            print(f"Error fetching balance: {e}")
            return None
