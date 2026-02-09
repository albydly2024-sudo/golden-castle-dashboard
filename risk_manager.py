"""
=======================================================
Risk Manager - Professional Risk Management
Phase 10: Component 6
=======================================================
"""

import config
from datetime import datetime, timedelta

class RiskManager:
    def __init__(self, initial_capital=10000):
        self.capital = initial_capital
        self.max_risk_per_trade = 0.02  # 2% per trade
        self.max_daily_loss = 0.05  # 5% max daily loss
        self.max_positions = 3
        
        self.daily_pnl = 0
        self.daily_reset_time = datetime.now().date()
        
    def calculate_position_size(self, entry_price, stop_loss_price, balance=None):
        """
        Calculate position size based on risk %.
        Formula: Position Size = (Account Risk) / (Entry - SL)
        """
        if balance is None:
            balance = self.capital
        
        risk_amount = balance * self.max_risk_per_trade
        price_risk = abs(entry_price - stop_loss_price)
        
        if price_risk == 0:
            return 0
        
        position_size = risk_amount / price_risk
        
        # Cap by Max Position Size (from Config)
        max_size_value = config.MAX_POSITION_SIZE
        if position_size * entry_price > max_size_value:
            position_size = max_size_value / entry_price
            
        # Cap by Available Balance (Spot)
        if position_size * entry_price > balance:
            position_size = (balance * 0.95) / entry_price # Leave 5% buffer for fees
            
        return round(position_size, 6)
    
    def check_daily_loss_limit(self):
        """
        Check if daily loss limit has been reached.
        """
        # Reset daily tracking if new day
        if datetime.now().date() > self.daily_reset_time:
            self.daily_pnl = 0
            self.daily_reset_time = datetime.now().date()
        
        max_loss = self.capital * self.max_daily_loss
        
        if self.daily_pnl < -max_loss:
            return True  # Limit reached
        
        return False
    
    def update_daily_pnl(self, pnl):
        """
        Update daily P/L tracking.
        """
        self.daily_pnl += pnl
    
    def get_portfolio_exposure(self, active_positions):
        """
        Calculate total portfolio exposure.
        """
        total_exposure = 0
        
        for symbol, position in active_positions.items():
            position_value = position['entry'] * position['size']
            total_exposure += position_value
        
        exposure_pct = (total_exposure / self.capital) * 100
        
        return {
            'total_value': round(total_exposure, 2),
            'percentage': round(exposure_pct, 2)
        }
    
    def can_open_position(self, active_positions_count):
        """
        Check if we can open a new position based on limits.
        """
        # Check daily loss limit
        if self.check_daily_loss_limit():
            print("⚠️ Daily loss limit reached. No new positions allowed.")
            return False
        
        # Check max positions
        if active_positions_count >= self.max_positions:
            print(f"⚠️ Max positions ({self.max_positions}) reached.")
            return False
        
        return True
    
    def calculate_risk_reward_ratio(self, entry, stop_loss, take_profit):
        """
        Calculate risk/reward ratio.
        """
        risk = abs(entry - stop_loss)
        reward = abs(take_profit - entry)
        
        if risk == 0:
            return 0
        
        ratio = reward / risk
        return round(ratio, 2)
    
    def get_risk_metrics(self):
        """
        Get current risk metrics for display.
        """
        return {
            'daily_pnl': round(self.daily_pnl, 2),
            'daily_pnl_pct': round((self.daily_pnl / self.capital) * 100, 2),
            'max_daily_loss': round(self.capital * self.max_daily_loss, 2),
            'risk_per_trade_pct': self.max_risk_per_trade * 100,
            'remaining_daily_risk': round((self.capital * self.max_daily_loss) + self.daily_pnl, 2)
        }


if __name__ == "__main__":
    # Example
    rm = RiskManager(initial_capital=10000)
    
    # Calculate position size
    entry = 50000
    sl = 49000
    size = rm.calculate_position_size(entry, sl)
    print(f"📊 Recommended position size: {size} BTC")
    
    # Check risk metrics
    metrics = rm.get_risk_metrics()
    print(f"💰 Daily P/L: ${metrics['daily_pnl']}")
    print(f"📉 Max Daily Loss: ${metrics['max_daily_loss']}")
