"""
=======================================================
Trade Executor - Automated Order Execution
Phase 10: Component 4
=======================================================
"""

import ccxt
import config
from datetime import datetime

class TradeExecutor:
    def __init__(self, client):
        self.client = client
        self.exchange = client.exchange
        self.active_positions = {}  # Track open positions
        
    def execute_market_order(self, symbol, side, amount):
        """
        Execute a market order.
        side: 'buy' or 'sell'
        amount: quantity in base currency
        """
        if not config.AUTO_TRADE_ENABLED:
            print(f"⚠️ Auto-trading is DISABLED. Would have executed: {side.upper()} {amount} {symbol}")
            return None
        
        try:
            print(f"🔄 Executing {side.upper()} order for {amount} {symbol}...")
            
            order = self.exchange.create_market_order(
                symbol=symbol,
                side=side,
                amount=amount
            )
            
            print(f"✅ Order executed: {order['id']}")
            return order
            
        except Exception as e:
            print(f"❌ Order execution failed: {e}")
            return None
    
    def set_stop_loss(self, symbol, side, amount, stop_price):
        """
        Set a stop-loss order.
        """
        if not config.AUTO_TRADE_ENABLED:
            print(f"⚠️ Auto-trading DISABLED. SL would be: {stop_price}")
            return None
        
        try:
            # Binance uses 'STOP_LOSS_LIMIT' order type
            order = self.exchange.create_order(
                symbol=symbol,
                type='stop_loss_limit',
                side='sell' if side == 'buy' else 'buy',
                amount=amount,
                price=stop_price,
                params={'stopPrice': stop_price}
            )
            
            print(f"✅ Stop Loss set at ${stop_price}")
            return order
            
        except Exception as e:
            print(f"❌ SL order failed: {e}")
            return None
    
    def set_take_profit(self, symbol, side, amount, tp_price):
        """
        Set a take-profit order.
        """
        if not config.AUTO_TRADE_ENABLED:
            print(f"⚠️ Auto-trading DISABLED. TP would be: {tp_price}")
            return None
        
        try:
            order = self.exchange.create_limit_order(
                symbol=symbol,
                side='sell' if side == 'buy' else 'buy',
                amount=amount,
                price=tp_price
            )
            
            print(f"✅ Take Profit set at ${tp_price}")
            return order
            
        except Exception as e:
            print(f"❌ TP order failed: {e}")
            return None
    
    def open_position(self, symbol, setup, position_size):
        """
        Open a full position with entry, SL, and TP.
        """
        side = 'buy' if setup['type'] == 'LONG' else 'sell'
        
        print(f"\n{'='*50}")
        print(f"🎯 Opening {setup['type']} position for {symbol}")
        print(f"{'='*50}")
        
        # 1. Execute market order
        entry_order = self.execute_market_order(symbol, side, position_size)
        
        if entry_order is None:
            print("❌ Position opening cancelled - entry order failed")
            return None
        
        # 2. Set Stop Loss
        sl_order = self.set_stop_loss(symbol, side, position_size, setup['stop_loss'])
        
        # 3. Set Take Profit
        tp_order = self.set_take_profit(symbol, side, position_size, setup['take_profit'])
        
        # Track position
        self.active_positions[symbol] = {
            'type': setup['type'],
            'entry': setup['entry'],
            'sl': setup['stop_loss'],
            'tp': setup['take_profit'],
            'size': position_size,
            'entry_order': entry_order,
            'sl_order': sl_order,
            'tp_order': tp_order,
            'opened_at': datetime.now()
        }
        
        print(f"✅ Position opened successfully!")
        return self.active_positions[symbol]
    
    def close_position(self, symbol):
        """
        Manually close an open position.
        """
        if symbol not in self.active_positions:
            print(f"⚠️ No active position for {symbol}")
            return None
        
        position = self.active_positions[symbol]
        side = 'sell' if position['type'] == 'LONG' else 'buy'
        
        # Execute market order to close
        close_order = self.execute_market_order(symbol, side, position['size'])
        
        if close_order:
            # Cancel SL/TP orders
            try:
                if position['sl_order']:
                    self.exchange.cancel_order(position['sl_order']['id'], symbol)
                if position['tp_order']:
                    self.exchange.cancel_order(position['tp_order']['id'], symbol)
            except:
                pass
            
            del self.active_positions[symbol]
            print(f"✅ Position closed for {symbol}")
            
        return close_order
    
    def get_position_status(self, symbol):
        """
        Get current status of a position.
        """
        if symbol not in self.active_positions:
            return None
        
        return self.active_positions[symbol]
