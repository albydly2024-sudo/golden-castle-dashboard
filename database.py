import os
import sqlite3
import pandas as pd
from datetime import datetime

# Version Tracer
print("DEBUG: Loading database.py v3 (Force Reload Fix)")

# Use absolute path to ensure consistency across imports
DB_NAME = os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_data.db")

def init_db():
    """Initializes the SQLite database with necessary tables."""
    print(f"DEBUG: Initializing database at {DB_NAME}")
    try:
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
            reason TEXT,
            status TEXT DEFAULT 'PENDING'
        )''')
        conn.row_factory = sqlite3.Row
        
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
        
        # NEW: Table for Active Positions (Persistent Tracking)
        c.execute('''CREATE TABLE IF NOT EXISTS active_positions (
            symbol TEXT PRIMARY KEY,
            type TEXT,
            entry_price REAL,
            stop_loss REAL,
            take_profit REAL,
            size REAL,
            highest_price REAL,
            opened_at TEXT
        )''')
        
        conn.commit()
        conn.close()
        print("DEBUG: Database initialized successfully.")
    except Exception as e:
        print(f"ERROR: Failed to initialize database: {e}")

def log_signal(symbol, type, price, sl, tp, reason, status='PENDING'):
    """Logs a new trade signal."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT INTO signals (timestamp, symbol, type, price, stop_loss, take_profit, reason, status)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''', 
              (timestamp, symbol, type, price, sl, tp, reason, status))
    conn.commit()
    conn.close()

def update_signal_status(signal_id, status):
    """Updates the status of a signal (APPROVED/REJECTED)."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE signals SET status=? WHERE id=?", (status, signal_id))
    conn.commit()
    conn.close()

def get_pending_signals():
    """Fetches all pending signals for approval."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql("SELECT * FROM signals WHERE status='PENDING' ORDER BY id DESC", conn)
        conn.close()
        return df
    except pd.errors.DatabaseError as e:
        if "no such table" in str(e):
            print("DEBUG: 'signals' table not found. Initializing database...")
            init_db()
            # Retry once
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql("SELECT * FROM signals WHERE status='PENDING' ORDER BY id DESC", conn)
            conn.close()
            return df
        else:
            raise

def get_approved_signals():
    """Fetches all signals approved by the user but not yet executed."""
    try:
        conn = sqlite3.connect(DB_NAME)
        df = pd.read_sql("SELECT * FROM signals WHERE status='APPROVED' ORDER BY id DESC", conn)
        conn.close()
        return df
    except pd.errors.DatabaseError as e:
        if "no such table" in str(e):
            print("DEBUG: 'signals' table not found. Initializing database...")
            init_db()
            # Retry once
            conn = sqlite3.connect(DB_NAME)
            df = pd.read_sql("SELECT * FROM signals WHERE status='APPROVED' ORDER BY id DESC", conn)
            conn.close()
            return df
        else:
            raise
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM signals WHERE status='APPROVED' ORDER BY id DESC", conn)
    conn.close()
    return df

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

# ===== Active Position Management =====

def save_active_position(symbol, pos_type, entry, sl, tp, size, highest):
    """Saves or updates an active position in the database."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    opened_at = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    c.execute('''INSERT OR REPLACE INTO active_positions 
                 (symbol, type, entry_price, stop_loss, take_profit, size, highest_price, opened_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?)''',
              (symbol, pos_type, entry, sl, tp, size, highest, opened_at))
    conn.commit()
    conn.close()

def get_active_positions():
    """Retrieves all active positions from the database."""
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql("SELECT * FROM active_positions", conn)
    conn.close()
    positions = {}
    for _, row in df.iterrows():
        positions[row['symbol']] = {
            'type': row['type'],
            'entry': row['entry_price'],
            'sl': row['stop_loss'],
            'tp': row['take_profit'],
            'size': row['size'],
            'highest_price': row['highest_price'],
            'opened_at': row['opened_at']
        }
    return positions

def remove_active_position(symbol):
    """Removes a position from active tracking."""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("DELETE FROM active_positions WHERE symbol=?", (symbol,))
    conn.commit()
    conn.close()
