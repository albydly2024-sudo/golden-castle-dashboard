import pandas as pd
import numpy as np

class Strategy:
    def __init__(self):
        # Strategy Parameters
        self.ema_trend_period = 200
        self.mtf_trend_period = 50  # For higher timeframe trend
        self.mav_short = 20
        self.risk_reward_ratio = 2.0
        self.atr_multiplier = 1.5
        self.volume_ma_period = 20
        self.volume_spike_multiplier = 1.5 # 50% above average

    def calculate_rsi(self, series, period=14):
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def apply_indicators(self, df):
        """
        Calculates advanced technical indicators using standard Pandas.
        No external 'ta' library needed.
        """
        close = df['close']

        # 1. Trend Filter: EMA 200
        df['EMA_200'] = close.ewm(span=self.ema_trend_period, adjust=False).mean()
        
        # 2. Momentum: MACD (12, 26, 9)
        k = close.ewm(span=12, adjust=False).mean()
        d = close.ewm(span=26, adjust=False).mean()
        df['MACD'] = k - d
        df['MACD_Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
        df['MACD_Hist'] = df['MACD'] - df['MACD_Signal']
        
        # 3. Volatility: Bollinger Bands (20, 2)
        sma_20 = close.rolling(window=20).mean()
        std_20 = close.rolling(window=20).std()
        df['BBL_20_2.0'] = sma_20 - (2 * std_20)
        df['BBU_20_2.0'] = sma_20 + (2 * std_20)

        # 4. RSI for extra confirmation
        # Note: wilder's smoothing is standard for RSI but simple rolling is close enough for this
        # or we implement wilder's. Let's start with a simple one for robustness.
        delta = close.diff()
        gain = (delta.where(delta > 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        loss = (-delta.where(delta < 0, 0)).ewm(alpha=1/14, adjust=False).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 5. Volatility for Risk Management: ATR (Average True Range)
        high = df['high']
        low = df['low']
        prev_close = close.shift(1)
        
        tr1 = high - low
        tr2 = (high - prev_close).abs()
        tr3 = (low - prev_close).abs()
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        df['ATR'] = tr.ewm(alpha=1/14, adjust=False).mean()

        # 6. Volume Moving Average
        df['Volume_MA'] = df['volume'].rolling(window=self.volume_ma_period).mean()

        return df

    def check_signal(self, df, df_mtf=None):
        """
        Generates trade signals with Multi-Timeframe (MTF) trend confirmation.
        """
        if len(df) < 200:
            return "NEUTRAL", None

        curr = df.iloc[-1]
        
        # Determine Higher Timeframe (MTF) Trend
        mtf_bias = "NEUTRAL"
        if df_mtf is not None and len(df_mtf) >= self.mtf_trend_period:
            mtf_close = df_mtf.iloc[-1]['close']
            mtf_ema = df_mtf['close'].ewm(span=self.mtf_trend_period, adjust=False).mean().iloc[-1]
            mtf_bias = "BULLISH" if mtf_close > mtf_ema else "BEARISH"
            
        signal = "NEUTRAL"
        setup = None

        # --- LONG (BUY) STRATEGY ---
        # 1. 1h Trend is UP
        is_uptrend = curr['close'] > curr['EMA_200']
        # 2. 4h Trend confirms (MTF)
        mtf_confirm_long = (mtf_bias == "BULLISH" or mtf_bias == "NEUTRAL") 
        # 3. Momentum is Positive
        is_momentum_up = curr['MACD'] > curr['MACD_Signal']
        # 4. Pullback Entry
        is_pullback = curr['low'] <= curr['BBL_20_2.0'] * 1.01
        
        # 5. Volume Spike
        is_volume_spike = curr['volume'] > (curr['Volume_MA'] * self.volume_spike_multiplier)
        
        # 6. Candle Close Confirmation (Last candle closed in direction)
        is_candle_bullish = curr['close'] > curr['open']
        is_candle_bearish = curr['close'] < curr['open']

        if is_uptrend and mtf_confirm_long and is_momentum_up and is_pullback and is_candle_bullish and is_volume_spike:
            signal = "BUY"
            stop_loss = curr['close'] - (curr['ATR'] * self.atr_multiplier)
            risk = curr['close'] - stop_loss
            take_profit = curr['close'] + (risk * self.risk_reward_ratio)
            
            setup = {
                "type": "LONG",
                "entry": curr['close'],
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": f"MTF {mtf_bias} + اتجاه صاعد + MACD إيجابي + حجم مرتفع ✅"
            }
        
        # --- SHORT (SELL) STRATEGY ---
        # 1. 1h Trend is DOWN
        is_downtrend = curr['close'] < curr['EMA_200']
        # 2. 4h Trend confirms (MTF)
        mtf_confirm_short = (mtf_bias == "BEARISH" or mtf_bias == "NEUTRAL")
        # 3. Momentum is Negative
        is_momentum_down = curr['MACD'] < curr['MACD_Signal']
        # 4. Bounce from Upper Bollinger Band
        is_bounce = curr['high'] >= curr['BBU_20_2.0'] * 0.99
        # 5. RSI Overbought
        is_overbought = curr['RSI'] > 70
        
        if is_downtrend and mtf_confirm_short and is_momentum_down and (is_bounce or is_overbought) and is_candle_bearish and is_volume_spike:
            signal = "SELL"
            stop_loss = curr['close'] + (curr['ATR'] * self.atr_multiplier)
            risk = stop_loss - curr['close']
            take_profit = curr['close'] - (risk * self.risk_reward_ratio)
            
            setup = {
                "type": "SHORT",
                "entry": curr['close'],
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "reason": f"MTF {mtf_bias} + اتجاه هابط + حجم مرتفع ✅"
            }
        
        return signal, setup
