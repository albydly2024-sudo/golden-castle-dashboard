import os
from dotenv import load_dotenv

# Streamlit secrets support
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False

def get_config(key, default=''):
    """Helper to get config from Streamlit Secrets or Environment Variables"""
    if HAS_STREAMLIT:
        try:
            return st.secrets.get(key, os.getenv(key, default))
        except:
            pass
    return os.getenv(key, default)

# Load .env file if it exists
load_dotenv()

# Binance API Configuration
# WARNING: Keep your keys secret!
API_KEY = get_config('API_KEY', '')
SECRET_KEY = get_config('SECRET_KEY', '')
BINANCE_TESTNET_ENABLED = str(get_config('BINANCE_TESTNET_ENABLED', 'True')).lower() == 'true'

# Cloud/Location Fix
# Cloud/Location Fix
# Set BINANCE_USE_US to 'True' if using Streamlit Cloud and get 451 Errors
# Default to True if we are in a headless environment (Cloud) and no API key is provided, assuming US restriction.
is_cloud = os.getenv('STREAMLIT_SERVER_HEADLESS', 'false').lower() == 'true'
default_us = 'True' if is_cloud and not API_KEY else 'False'

BINANCE_USE_US = str(get_config('BINANCE_USE_US', default_us)).lower() == 'true'
BINANCE_PROXY = get_config('BINANCE_PROXY', None) # e.g. "http://user:pass@host:port"

if BINANCE_USE_US:
    print("🇺🇸 US Mode Auto-Enabled due to Cloud/Missing Keys")

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
