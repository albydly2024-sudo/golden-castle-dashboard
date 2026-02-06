import sqlite3
import pandas as pd
from datetime import datetime

DB_NAME = "bot_data.db"

def init_db():
    """Initializes the SQLite database with necessary tables."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    # Table for Signals
    c.execute('''CREATE TABLE IF NOT EXISTS signals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT,
        symbol TEXT,
        type TEXT,
        price REAL,
        stop_loss REAL,
        take_profit REAL,
        reason TEXT
    )''')
    
    # Table for Market Status (Snapshot for Dashboard)
    c.execute('''CREATE TABLE IF NOT EXISTS market_status (
        symbol TEXT PRIMARY KEY,
        timestamp TEXT,
        price REAL,
        trend TEXT,
        rsi REAL,
        last_updated TEXT
    )''')
    
    # Phase 10: Table for Completed Trades
    c.execute('''CREATE TABLE IF NOT EXISTS trades (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT,
        type TEXT,
        entry_time TEXT,
        exit_time TEXT,
        entry_price REAL,
        exit_price REAL,
        size REAL,
        profit_loss REAL,
        profit_pct REAL,
        exit_reason TEXT
    )''')
    
    conn.commit()
    conn.close()

def log_signal(symbol, type, price, sl, tp, reason):
    """Logs a new trade signal."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO signals (timestamp, symbol, type, price, stop_loss, take_profit, reason)
                 VALUES (?, ?, ?, ?, ?, ?, ?)''', 
              (timestamp, symbol, type, price, sl, tp, reason))
    conn.commit()
    conn.close()

def update_market_status(symbol, price, trend, rsi):
    """Updates the latest status for a coin."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    c.execute('''INSERT OR REPLACE INTO market_status (symbol, timestamp, price, trend, rsi, last_updated)
                 VALUES (?, ?, ?, ?, ?, ?)''',
              (symbol, timestamp, price, trend, rsi, timestamp))
    conn.commit()
    conn.close()

def get_recent_signals(limit=10):
    """Fetches recent signals for the dashboard."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM signals ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def get_market_status():
    """Fetches latest market status for all coins."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM market_status", conn)
    conn.close()
    return df

# ===== Phase 10: Performance Tracking =====

def log_trade(symbol, type, entry_time, exit_time, entry_price, exit_price, size, profit_loss, exit_reason):
    """Log a completed trade."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    
    profit_pct = (profit_loss / (entry_price * size)) * 100
    
    c.execute('''INSERT INTO trades (symbol, type, entry_time, exit_time, entry_price, exit_price, size, profit_loss, profit_pct, exit_reason)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)''',
              (symbol, type, entry_time, exit_time, entry_price, exit_price, size, profit_loss, profit_pct, exit_reason))
    conn.commit()
    conn.close()

def get_trade_history(limit=50):
    """Get trade history."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql(f"SELECT * FROM trades ORDER BY id DESC LIMIT {limit}", conn)
    conn.close()
    return df

def calculate_stats():
    """Calculate performance statistics."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM trades", conn)
    conn.close()
   
    if df.empty:
        return {
            'total_trades': 0,
            'total_pnl': 0,
            'win_rate': 0,
            'best_trade': 0,
            'worst_trade': 0,
            'avg_profit': 0
        }
    
    total_trades = len(df)
    total_pnl = df['profit_loss'].sum()
    winners = df[df['profit_loss'] > 0]
    win_rate = (len(winners) / total_trades * 100) if total_trades > 0 else 0
    best_trade = df['profit_loss'].max()
    worst_trade = df['profit_loss'].min()
    avg_profit = df['profit_loss'].mean()
    
    return {
        'total_trades': total_trades,
        'total_pnl': round(total_pnl, 2),
        'win_rate': round(win_rate, 2),
        'best_trade': round(best_trade, 2),
        'worst_trade': round(worst_trade, 2),
        'avg_profit': round(avg_profit, 2)
    }
