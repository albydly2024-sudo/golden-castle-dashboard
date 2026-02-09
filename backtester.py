"""
=======================================================
Backtesting Engine - Professional Strategy Testing
Phase 10: Component 1
=======================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from market_data import BinanceClient
from strategy import Strategy
import config

class Backtester:
    def __init__(self, initial_capital=10000):
        self.initial_capital = initial_capital
        self.client = BinanceClient()
        self.strategy = Strategy()
        
    def load_historical_data(self, symbol, days=365):
        """
        Load historical data for backtesting.
        """
        print(f"📥 Loading {days} days of historical data for {symbol}...")
        
        # Fetch data (approx 24 candles per day for 1h timeframe)
        limit = days * 24
        df = self.client.fetch_data(symbol, '1h', limit)
        
        if df is None or df.empty:
            print(f"❌ Failed to load data for {symbol}")
            return None
            
        print(f"✅ Loaded {len(df)} candles")
        return df
    
    def run_backtest(self, symbol, df, df_mtf=None):
        """
        Run backtest on historical data.
        Returns trade log and equity curve.
        """
        print(f"\n🚀 Starting Backtest for {symbol}...")
        print("="*50)
        
        # Apply indicators
        df = self.strategy.apply_indicators(df)
        
        # Initialize tracking
        trades = []
        equity_curve = [self.initial_capital]
        current_capital = self.initial_capital
        position = None  # {type, entry, sl, tp, size}
        
        # Simulate trading
        for i in range(200, len(df)):  # Start after indicator warmup
            current_bar = df.iloc[i]
            current_price = current_bar['close']
            timestamp = current_bar['timestamp']
            
            # Check if we have an open position
            if position:
                # Check Stop Loss
                if position['type'] == 'LONG' and current_bar['low'] <= position['sl']:
                    # SL Hit
                    exit_price = position['sl']
                    pnl = (exit_price - position['entry']) * position['size']
                    current_capital += pnl
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': timestamp,
                        'type': position['type'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'exit_reason': 'SL'
                    })
                    position = None
                    
                elif position['type'] == 'SELL' and current_bar['high'] >= position['sl']:
                    # SL Hit
                    exit_price = position['sl']
                    pnl = (position['entry'] - exit_price) * position['size']
                    current_capital += pnl
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': timestamp,
                        'type': position['type'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'exit_reason': 'SL'
                    })
                    position = None
                
                # Check Take Profit
                elif position['type'] == 'LONG' and current_bar['high'] >= position['tp']:
                    # TP Hit
                    exit_price = position['tp']
                    pnl = (exit_price - position['entry']) * position['size']
                    current_capital += pnl
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': timestamp,
                        'type': position['type'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'exit_reason': 'TP'
                    })
                    position = None
                    
                elif position['type'] == 'SELL' and current_bar['low'] <= position['tp']:
                    # TP Hit
                    exit_price = position['tp']
                    pnl = (position['entry'] - exit_price) * position['size']
                    current_capital += pnl
                    
                    trades.append({
                        'entry_time': position['entry_time'],
                        'exit_time': timestamp,
                        'type': position['type'],
                        'entry': position['entry'],
                        'exit': exit_price,
                        'pnl': pnl,
                        'exit_reason': 'TP'
                    })
                    position = None
            
            # If no position, check for new signals
            if not position:
                signal, setup = self.strategy.check_signal(df.iloc[:i+1], df_mtf)
                
                if signal in ['BUY', 'SELL'] and setup:
                    # Calculate position size (simple: 10% of capital per trade)
                    risk_per_trade = current_capital * 0.10
                    position_size = risk_per_trade / current_price
                    
                    position = {
                        'type': signal,
                        'entry': setup['entry'],
                        'sl': setup['stop_loss'],
                        'tp': setup['take_profit'],
                        'size': position_size,
                        'entry_time': timestamp
                    }
            
            # Track equity
            if position:
                # Mark-to-market
                if position['type'] == 'LONG':
                    unrealized_pnl = (current_price - position['entry']) * position['size']
                else:
                    unrealized_pnl = (position['entry'] - current_price) * position['size']
                equity_curve.append(current_capital + unrealized_pnl)
            else:
                equity_curve.append(current_capital)
        
        return trades, equity_curve
    
    def calculate_metrics(self, trades, equity_curve):
        """
        Calculate performance metrics.
        """
        if not trades:
            return {
                'total_trades': 0,
                'winning_trades': 0,
                'losing_trades': 0,
                'win_rate': 0,
                'profit_factor': 0,
                'max_drawdown': 0,
                'total_pnl': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'final_capital': self.initial_capital,
                'return_pct': 0
            }
        
        trades_df = pd.DataFrame(trades)
        
        # Basic Stats
        total_trades = len(trades_df)
        winning_trades = trades_df[trades_df['pnl'] > 0]
        losing_trades = trades_df[trades_df['pnl'] < 0]
        
        win_rate = (len(winning_trades) / total_trades * 100) if total_trades > 0 else 0
        
        total_wins = winning_trades['pnl'].sum() if len(winning_trades) > 0 else 0
        total_losses = abs(losing_trades['pnl'].sum()) if len(losing_trades) > 0 else 0
        
        profit_factor = (total_wins / total_losses) if total_losses > 0 else 0
        
        # Max Drawdown
        equity_series = pd.Series(equity_curve)
        running_max = equity_series.expanding().max()
        drawdown = (equity_series - running_max) / running_max * 100
        max_drawdown = drawdown.min()
        
        total_pnl = trades_df['pnl'].sum()
        avg_win = winning_trades['pnl'].mean() if len(winning_trades) > 0 else 0
        avg_loss = losing_trades['pnl'].mean() if len(losing_trades) > 0 else 0
        
        return {
            'total_trades': total_trades,
            'winning_trades': len(winning_trades),
            'losing_trades': len(losing_trades),
            'win_rate': round(win_rate, 2),
            'profit_factor': round(profit_factor, 2),
            'max_drawdown': round(max_drawdown, 2),
            'total_pnl': round(total_pnl, 2),
            'avg_win': round(avg_win, 2),
            'avg_loss': round(avg_loss, 2),
            'final_capital': round(equity_curve[-1], 2),
            'return_pct': round((equity_curve[-1] - self.initial_capital) / self.initial_capital * 100, 2)
        }
    
    def print_results(self, metrics):
        """
        Print backtest results in Arabic.
        """
        print("\n" + "="*50)
        print("📊 نتائج اختبار الاستراتيجية")
        print("="*50)
        print(f"📈 إجمالي الصفقات: {metrics['total_trades']}")
        print(f"✅ صفقات رابحة: {metrics['winning_trades']}")
        print(f"❌ صفقات خاسرة: {metrics['losing_trades']}")
        print(f"🎯 نسبة النجاح: {metrics['win_rate']}%")
        print(f"💰 معامل الربح: {metrics['profit_factor']}")
        print(f"📉 أقصى انخفاض: {metrics['max_drawdown']}%")
        print(f"💵 إجمالي الربح/الخسارة: ${metrics['total_pnl']}")
        print(f"📊 متوسط الربح: ${metrics['avg_win']}")
        print(f"📊 متوسط الخسارة: ${metrics['avg_loss']}")
        print(f"🏆 رأس المال النهائي: ${metrics['final_capital']}")
        print(f"📈 العائد: {metrics['return_pct']}%")
        print("="*50)


if __name__ == "__main__":
    # Example usage
    backtester = Backtester(initial_capital=10000)
    
    symbol = 'BTC/USDT'
    df = backtester.load_historical_data(symbol, days=180)
    
    if df is not None:
        trades, equity = backtester.run_backtest(symbol, df)
        metrics = backtester.calculate_metrics(trades, equity)
        backtester.print_results(metrics)
