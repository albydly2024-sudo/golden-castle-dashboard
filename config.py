import os
from dotenv import load_dotenv

# Load .env file if it exists
load_dotenv()

# Binance API Configuration
# WARNING: Keep your keys secret!
API_KEY = os.getenv('API_KEY', '')
SECRET_KEY = os.getenv('SECRET_KEY', '')
BINANCE_TESTNET_ENABLED = os.getenv('BINANCE_TESTNET_ENABLED', 'True') == 'True'

# Cloud/Location Fix
# Set BINANCE_USE_US to 'True' if using Streamlit Cloud and get 451 Errors
BINANCE_USE_US = os.getenv('BINANCE_USE_US', 'False') == 'True'
BINANCE_PROXY = os.getenv('BINANCE_PROXY', None) # e.g. "http://user:pass@host:port"

# Bot Settings
# All prices from Binance (Real-time, matches your account)
TARGET_PAIRS = ['PAXG/USDT', 'BTC/USDT', 'ETH/USDT', 'BNB/USDT', 'SOL/USDT', 'XRP/USDT', 'DOGE/USDT']
TIMEFRAME = '1h'  # 1m, 5m, 15m, 1h, 4h, 1d
LIMIT = 300       # Number of candles to fetch

# Telegram Settings
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN', 'YOUR_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID', 'YOUR_CHAT_ID')

# ===== Phase 10: Professional Trading Settings =====
# Auto-Trading (set to True to enable REAL orders)
AUTO_TRADE_ENABLED = True  # 🚀 ENABLED: Automatic execution is active

# Risk Management
MAX_POSITION_SIZE = 1000  # Max $ per position
RISK_PER_TRADE = 0.02  # 2% risk per trade
MAX_DAILY_LOSS = 0.05  # 5% max daily loss
MAX_POSITIONS = 3  # Maximum concurrent positions

# Trading Capital
TRADING_CAPITAL = 10000  # Starting capital for risk calculations
