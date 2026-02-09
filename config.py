import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    EXCHANGE_NAME = os.getenv('EXCHANGE_NAME', 'binance')
    API_KEY = os.getenv('API_KEY')
    SECRET_KEY = os.getenv('SECRET_KEY')
    SYMBOL = os.getenv('TRADING_SYMBOL', 'BTC/USDT')
    ORDER_SIZE_P = float(os.getenv('ORDER_SIZE_PERCENT', 5))
    STOP_LOSS_P = float(os.getenv('STOP_LOSS_PERCENT', 2))
    TAKE_PROFIT_P = float(os.getenv('TAKE_PROFIT_PERCENT', 4))
    MODE = os.getenv('TRADING_MODE', 'paper') # 'paper' or 'live'
    
    # Phase 7: Elite Features
    MAX_OPEN_TRADES = int(os.getenv('MAX_OPEN_TRADES', 3))
    TP_TARGETS = [1.5, 3.5] # Multi-TP targets (%)
    BREAK_EVEN_P = float(os.getenv('BREAK_EVEN_P', 1.2)) # Move SL to entry at 1.2% profit
    
    # Phase 8: AI & Capital
    AUTO_COMPOUND = os.getenv('AUTO_COMPOUND', 'true').lower() == 'true'
    WHALE_VOL_MULTIPLIER = float(os.getenv('WHALE_VOL_MULTIPLIER', 3.0)) # 3x avg volume = whale
    PUBLIC_MODE = os.getenv('PUBLIC_MODE', 'true').lower() == 'true'

    # Telegram Config
    TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
    TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID') # Primary Owner
    # List of all authorized IDs (Comma separated in .env)
    auth_env = os.getenv('AUTHORIZED_USERS', TELEGRAM_CHAT_ID or "")
    AUTHORIZED_USERS = [id.strip() for id in auth_env.split(',') if id.strip()]

    @classmethod
    def validate(cls):
        if cls.MODE == 'live' and (not cls.API_KEY or not cls.SECRET_KEY):
            raise ValueError("API Keys are required for LIVE trading.")
        print(f"--- Config Loaded: {cls.EXCHANGE_NAME} | {cls.SYMBOL} | Mode: {cls.MODE} ---")

config = Config()
