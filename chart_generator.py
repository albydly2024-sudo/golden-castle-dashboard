"""
=======================================================
Chart Generator for Telegram Alerts
Phase 10: Component 2
=======================================================
"""

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import pandas as pd
from datetime import datetime
import os

class ChartGenerator:
    def __init__(self):
        self.temp_dir = 'temp_charts'
        if not os.path.exists(self.temp_dir):
            os.makedirs(self.temp_dir)
    
    def generate_signal_chart(self, df, symbol, setup):
        """
        Generate a professional chart with entry, SL, and TP marked.
        Returns: Path to saved PNG file
        """
        # Set style
        plt.style.use('dark_background')
        
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 8), 
                                        gridspec_kw={'height_ratios': [3, 1]})
        
        # === Subplot 1: Price + Indicators ===
        # Plot candlesticks (simplified as line for now)
        ax1.plot(df['timestamp'], df['close'], color='#FFD700', linewidth=2, label='السعر')
        
        # EMA 200
        if 'EMA_200' in df.columns:
            ax1.plot(df['timestamp'], df['EMA_200'], 
                    color='#00d4ff', linewidth=1.5, alpha=0.7, label='EMA 200')
        
        # Bollinger Bands
        if 'BBU_20_2.0' in df.columns:
            ax1.plot(df['timestamp'], df['BBU_20_2.0'], 
                    color='#888', linewidth=1, linestyle='--', alpha=0.5)
            ax1.plot(df['timestamp'], df['BBL_20_2.0'], 
                    color='#888', linewidth=1, linestyle='--', alpha=0.5)
            ax1.fill_between(df['timestamp'], df['BBL_20_2.0'], df['BBU_20_2.0'],
                            color='#00d4ff', alpha=0.1)
        
        # Mark Entry, SL, TP
        entry_price = setup['entry']
        sl_price = setup['stop_loss']
        tp_price = setup['take_profit']
        signal_type = setup['type']
        
        # Entry point
        ax1.axhline(y=entry_price, color='#FFD700', linewidth=2, 
                   linestyle='-', label=f'دخول: ${entry_price:.2f}')
        
        # Stop Loss
        ax1.axhline(y=sl_price, color='#ff4444', linewidth=2, 
                   linestyle='--', label=f'إيقاف الخسارة: ${sl_price:.2f}')
        
        # Take Profit
        ax1.axhline(y=tp_price, color='#00ff88', linewidth=2, 
                   linestyle='--', label=f'جني الأرباح: ${tp_price:.2f}')
        
        # Styling
        ax1.set_title(f'🚀 {signal_type} Signal: {symbol}', fontsize=16, color='#FFD700', weight='bold')
        ax1.set_ylabel('السعر (USDT)', fontsize=12, color='#fff')
        ax1.legend(loc='upper left', fontsize=10)
        ax1.grid(True, alpha=0.2)
        ax1.set_facecolor('#0a0a0a')
        
        # === Subplot 2: MACD ===
        if 'MACD' in df.columns:
            # MACD Histogram
            colors = ['#00ff88' if val >= 0 else '#ff4444' for val in df['MACD_Hist']]
            ax2.bar(df['timestamp'], df['MACD_Hist'], color=colors, alpha=0.7, width=0.02)
            
            # MACD Lines
            ax2.plot(df['timestamp'], df['MACD'], color='#00d4ff', linewidth=1.5, label='MACD')
            ax2.plot(df['timestamp'], df['MACD_Signal'], color='#FFD700', linewidth=1.5, label='Signal')
            ax2.axhline(y=0, color='#fff', linewidth=0.5, linestyle='-', alpha=0.3)
        
        ax2.set_xlabel('الوقت', fontsize=12, color='#fff')
        ax2.set_ylabel('MACD', fontsize=12, color='#fff')
        ax2.legend(loc='upper left', fontsize=9)
        ax2.grid(True, alpha=0.2)
        ax2.set_facecolor('#0a0a0a')
        
        # Save
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'{self.temp_dir}/{symbol.replace("/", "_")}_{signal_type}_{timestamp}.png'
        
        plt.tight_layout()
        plt.savefig(filename, dpi=150, facecolor='#0a0a0a')
        plt.close()
        
        print(f"📸 Chart saved: {filename}")
        return filename
    
    def cleanup_old_charts(self, max_age_hours=24):
        """Remove charts older than specified hours."""
        import time
        now = time.time()
        
        for filename in os.listdir(self.temp_dir):
            filepath = os.path.join(self.temp_dir, filename)
            if os.path.isfile(filepath):
                file_age = now - os.path.getmtime(filepath)
                if file_age > (max_age_hours * 3600):
                    os.remove(filepath)
                    print(f"🗑️ Removed old chart: {filename}")


if __name__ == "__main__":
    # Test
    from market_data import BinanceClient
    from strategy import Strategy
    
    client = BinanceClient()
    strategy = Strategy()
    
    df = client.fetch_data('BTC/USDT', '1h', 100)
    if df is not None:
        df = strategy.apply_indicators(df)
        
        # Mock setup
        setup = {
            'type': 'LONG',
            'entry': df.iloc[-1]['close'],
            'stop_loss': df.iloc[-1]['close'] * 0.97,
            'take_profit': df.iloc[-1]['close'] * 1.05
        }
        
        generator = ChartGenerator()
        chart_path = generator.generate_signal_chart(df, 'BTC/USDT', setup)
        print(f"✅ Test chart created: {chart_path}")
