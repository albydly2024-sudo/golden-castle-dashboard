"""
=======================================================
🥇 Professional Gold Analyzer v2.0 - القلعة الذهبية
Institutional-Grade Gold Analysis System
Multi-Timeframe + Advanced Scoring + Market Sentiment
=======================================================
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


class GoldAnalyzer:
    """Institutional-grade Gold Analyzer with advanced metrics."""
    
    def __init__(self):
        self.symbol = 'PAXG/USDT'
        
        # Weight configuration for confidence scoring
        self.weights = {
            'trend': 25,
            'momentum': 20,
            'rsi': 15,
            'bollinger': 15,
            'pivot': 10,
            'volume': 10,
            'pattern': 5
        }
        
    def calculate_pivot_points(self, df):
        """Calculate Pivot Points with Camarilla and Woodie levels."""
        if len(df) < 2:
            return {}
        
        prev = df.iloc[-2]
        high = prev['high']
        low = prev['low']
        close = prev['close']
        open_price = prev['open']
        
        # Standard Pivot
        pivot = (high + low + close) / 3
        
        # Standard S/R
        r1 = (2 * pivot) - low
        r2 = pivot + (high - low)
        r3 = high + 2 * (pivot - low)
        s1 = (2 * pivot) - high
        s2 = pivot - (high - low)
        s3 = low - 2 * (high - pivot)
        
        # Woodie Pivot
        woodie_pivot = (high + low + 2 * close) / 4
        
        # Camarilla Levels (more precise for intraday)
        range_hl = high - low
        cam_r4 = close + range_hl * 1.1 / 2
        cam_r3 = close + range_hl * 1.1 / 4
        cam_s3 = close - range_hl * 1.1 / 4
        cam_s4 = close - range_hl * 1.1 / 2
        
        return {
            'pivot': round(pivot, 2),
            'r1': round(r1, 2),
            'r2': round(r2, 2),
            'r3': round(r3, 2),
            's1': round(s1, 2),
            's2': round(s2, 2),
            's3': round(s3, 2),
            'woodie': round(woodie_pivot, 2),
            'cam_r3': round(cam_r3, 2),
            'cam_r4': round(cam_r4, 2),
            'cam_s3': round(cam_s3, 2),
            'cam_s4': round(cam_s4, 2)
        }
    
    def calculate_fibonacci_levels(self, df, lookback=50):
        """Calculate Fibonacci levels with extension targets."""
        if len(df) < lookback:
            return {}
        
        recent = df.tail(lookback)
        high = recent['high'].max()
        low = recent['low'].min()
        diff = high - low
        
        return {
            'high': round(high, 2),
            'low': round(low, 2),
            'fib_236': round(high - (diff * 0.236), 2),
            'fib_382': round(high - (diff * 0.382), 2),
            'fib_500': round(high - (diff * 0.500), 2),
            'fib_618': round(high - (diff * 0.618), 2),
            'fib_786': round(high - (diff * 0.786), 2),
            # Extension levels for targets
            'ext_1272': round(high + (diff * 0.272), 2),
            'ext_1618': round(high + (diff * 0.618), 2)
        }
    
    def analyze_trend_strength(self, df):
        """Advanced trend analysis with multiple EMAs and ADX-like scoring."""
        if len(df) < 200:
            return {"strength": 0, "direction": "غير محدد", "icon": "⚪"}
        
        curr = df.iloc[-1]
        close = curr['close']
        
        # Calculate multiple EMAs
        ema_9 = df['close'].ewm(span=9, adjust=False).mean().iloc[-1]
        ema_21 = df['close'].ewm(span=21, adjust=False).mean().iloc[-1]
        ema_50 = df['close'].ewm(span=50, adjust=False).mean().iloc[-1]
        ema_100 = df['close'].ewm(span=100, adjust=False).mean().iloc[-1]
        ema_200 = curr['EMA_200']
        
        # Trend scoring (0-100)
        score = 0
        
        # Price position relative to EMAs
        if close > ema_9: score += 10
        if close > ema_21: score += 10
        if close > ema_50: score += 15
        if close > ema_100: score += 15
        if close > ema_200: score += 20
        
        # EMA alignment (golden cross pattern)
        if ema_9 > ema_21: score += 10
        if ema_21 > ema_50: score += 10
        if ema_50 > ema_200: score += 10
        
        # Determine direction and icon
        if score >= 80:
            return {"strength": score, "direction": "صعود قوي جداً", "icon": "🟢🟢", "bias": "شراء قوي"}
        elif score >= 60:
            return {"strength": score, "direction": "صعود قوي", "icon": "🟢", "bias": "شراء"}
        elif score >= 40:
            return {"strength": score, "direction": "صعود ضعيف", "icon": "🟡", "bias": "محايد صاعد"}
        elif score >= 30:
            return {"strength": score, "direction": "محايد", "icon": "⚪", "bias": "محايد"}
        elif score >= 20:
            return {"strength": score, "direction": "هبوط ضعيف", "icon": "🟠", "bias": "محايد هابط"}
        else:
            return {"strength": score, "direction": "هبوط قوي", "icon": "🔴", "bias": "بيع"}
    
    def analyze_momentum(self, df):
        """Analyze momentum using RSI, MACD, and Stochastic-like calculation."""
        if len(df) < 50:
            return {}
        
        curr = df.iloc[-1]
        prev = df.iloc[-2]
        
        rsi = curr['RSI']
        macd = curr['MACD']
        macd_signal = curr['MACD_Signal']
        macd_hist = curr['MACD_Hist']
        prev_macd_hist = prev['MACD_Hist']
        
        # RSI Analysis
        if rsi > 80:
            rsi_status = "تشبع شرائي حاد ⚠️"
            rsi_score = -20
        elif rsi > 70:
            rsi_status = "تشبع شرائي"
            rsi_score = -10
        elif rsi < 20:
            rsi_status = "تشبع بيعي حاد ⚠️"
            rsi_score = 20
        elif rsi < 30:
            rsi_status = "تشبع بيعي"
            rsi_score = 10
        elif 45 <= rsi <= 55:
            rsi_status = "متوازن"
            rsi_score = 0
        elif rsi > 55:
            rsi_status = "زخم إيجابي"
            rsi_score = 5
        else:
            rsi_status = "زخم سلبي"
            rsi_score = -5
        
        # MACD Analysis
        macd_bullish = macd > macd_signal
        macd_increasing = macd_hist > prev_macd_hist
        
        if macd_bullish and macd_increasing:
            macd_status = "إيجابي متزايد 📈"
            macd_score = 20
        elif macd_bullish:
            macd_status = "إيجابي"
            macd_score = 10
        elif not macd_bullish and not macd_increasing:
            macd_status = "سلبي متزايد 📉"
            macd_score = -20
        else:
            macd_status = "سلبي"
            macd_score = -10
        
        # Overall momentum score
        momentum_score = max(0, min(100, 50 + rsi_score + macd_score))
        
        return {
            'rsi': round(rsi, 1),
            'rsi_status': rsi_status,
            'macd_status': macd_status,
            'macd_bullish': macd_bullish,
            'momentum_score': momentum_score,
            'momentum_status': "إيجابي 🟢" if momentum_score > 55 else "سلبي 🔴" if momentum_score < 45 else "محايد ⚪"
        }
    
    def calculate_volatility(self, df, period=14):
        """Advanced volatility analysis."""
        if len(df) < period:
            return {}
        
        curr = df.iloc[-1]
        atr = curr['ATR'] if 'ATR' in df.columns else 0
        close = curr['close']
        
        # ATR as percentage
        atr_pct = (atr / close) * 100 if close > 0 else 0
        
        # Historical volatility (20-period standard deviation of returns)
        returns = df['close'].pct_change().tail(20)
        hist_vol = returns.std() * 100 * np.sqrt(252)  # Annualized
        
        # Bollinger Band Width
        bb_upper = curr['BBU_20_2.0']
        bb_lower = curr['BBL_20_2.0']
        bb_width = ((bb_upper - bb_lower) / close) * 100
        
        if atr_pct > 2.5:
            status = "⚠️ تقلب شديد جداً"
            risk_level = "عالي جداً"
        elif atr_pct > 1.5:
            status = "تقلب عالي"
            risk_level = "عالي"
        elif atr_pct > 0.8:
            status = "تقلب متوسط"
            risk_level = "متوسط"
        else:
            status = "تقلب منخفض"
            risk_level = "منخفض"
        
        return {
            'atr': round(atr, 2),
            'atr_pct': round(atr_pct, 2),
            'bb_width': round(bb_width, 2),
            'hist_vol': round(hist_vol, 1),
            'status': status,
            'risk_level': risk_level
        }
    
    def generate_professional_recommendation(self, df):
        """Generate institutional-grade trading recommendation."""
        if len(df) < 200:
            return None
        
        curr = df.iloc[-1]
        close = curr['close']
        atr = curr['ATR'] if 'ATR' in df.columns else close * 0.01
        
        # Get all analyses
        trend = self.analyze_trend_strength(df)
        momentum = self.analyze_momentum(df)
        volatility = self.calculate_volatility(df)
        pivots = self.calculate_pivot_points(df)
        fib = self.calculate_fibonacci_levels(df)
        
        # === Advanced Confidence Scoring ===
        buy_score = 0
        sell_score = 0
        reasons_buy = []
        reasons_sell = []
        
        # 1. Trend Analysis (25 points max)
        trend_strength = trend['strength']
        if trend_strength >= 70:
            buy_score += 25
            reasons_buy.append(f"اتجاه صاعد قوي ({trend_strength}%)")
        elif trend_strength >= 50:
            buy_score += 15
            reasons_buy.append(f"اتجاه صاعد ({trend_strength}%)")
        elif trend_strength <= 30:
            sell_score += 25
            reasons_sell.append(f"اتجاه هابط قوي ({100-trend_strength}%)")
        elif trend_strength <= 40:
            sell_score += 15
            reasons_sell.append(f"اتجاه هابط ({100-trend_strength}%)")
        
        # 2. Momentum Analysis (20 points max)
        mom_score = momentum.get('momentum_score', 50)
        if mom_score >= 65:
            buy_score += 20
            reasons_buy.append(f"زخم إيجابي قوي ({momentum['rsi_status']})")
        elif mom_score >= 55:
            buy_score += 10
            reasons_buy.append("زخم إيجابي")
        elif mom_score <= 35:
            sell_score += 20
            reasons_sell.append(f"زخم سلبي قوي ({momentum['rsi_status']})")
        elif mom_score <= 45:
            sell_score += 10
            reasons_sell.append("زخم سلبي")
        
        # 3. RSI Extreme Zones (15 points max)
        rsi = momentum.get('rsi', 50)
        if rsi < 25:
            buy_score += 15
            reasons_buy.append("RSI في منطقة ذهبية للشراء (<25)")
        elif rsi < 35:
            buy_score += 10
            reasons_buy.append("RSI في منطقة تشبع بيعي")
        elif rsi > 75:
            sell_score += 15
            reasons_sell.append("RSI في منطقة خطر البيع (>75)")
        elif rsi > 65:
            sell_score += 10
            reasons_sell.append("RSI في منطقة تشبع شرائي")
        
        # 4. Bollinger Band Position (15 points max)
        bb_lower = curr['BBL_20_2.0']
        bb_upper = curr['BBU_20_2.0']
        bb_mid = (bb_upper + bb_lower) / 2
        
        if close <= bb_lower * 1.005:
            buy_score += 15
            reasons_buy.append("السعر عند الحد السفلي للبولنجر")
        elif close < bb_mid:
            buy_score += 5
        
        if close >= bb_upper * 0.995:
            sell_score += 15
            reasons_sell.append("السعر عند الحد العلوي للبولنجر")
        elif close > bb_mid:
            sell_score += 5
        
        # 5. Pivot Support/Resistance (10 points max)
        if pivots:
            s1, r1 = pivots.get('s1', 0), pivots.get('r1', float('inf'))
            if close <= s1 * 1.005:
                buy_score += 10
                reasons_buy.append(f"السعر عند دعم S1 (${s1:,.0f})")
            if close >= r1 * 0.995:
                sell_score += 10
                reasons_sell.append(f"السعر عند مقاومة R1 (${r1:,.0f})")
        
        # 6. MACD Crossover (10 points max)
        if momentum.get('macd_bullish'):
            buy_score += 10
            reasons_buy.append("تقاطع MACD إيجابي")
        else:
            sell_score += 10
            reasons_sell.append("تقاطع MACD سلبي")
        
        # === Determine Final Signal ===
        total_possible = 95
        buy_confidence = min(99, int((buy_score / total_possible) * 100))
        sell_confidence = min(99, int((sell_score / total_possible) * 100))
        
        # Minimum threshold for signal
        THRESHOLD = 40
        
        if buy_confidence >= THRESHOLD and buy_confidence > sell_confidence + 15:
            signal = "شراء"
            signal_icon = "🟢"
            confidence = buy_confidence
            reasons = reasons_buy[:5]  # Top 5 reasons
            
            # Calculate levels
            entry = close
            stop_loss = close - (atr * 2)
            take_profit_1 = close + (atr * 2)
            take_profit_2 = close + (atr * 4)
            take_profit_3 = close + (atr * 6)
            
        elif sell_confidence >= THRESHOLD and sell_confidence > buy_confidence + 15:
            signal = "بيع"
            signal_icon = "🔴"
            confidence = sell_confidence
            reasons = reasons_sell[:5]
            
            entry = close
            stop_loss = close + (atr * 2)
            take_profit_1 = close - (atr * 2)
            take_profit_2 = close - (atr * 4)
            take_profit_3 = close - (atr * 6)
            
        else:
            signal = "انتظار"
            signal_icon = "⏳"
            confidence = max(buy_confidence, sell_confidence)
            reasons = (reasons_buy + reasons_sell)[:3]
            reasons.append("لا توجد إشارات واضحة - انتظر فرصة أفضل")
            
            entry = close
            stop_loss = close - (atr * 2)
            take_profit_1 = close + (atr * 2)
            take_profit_2 = close + (atr * 4)
            take_profit_3 = close + (atr * 6)
        
        # Risk calculation
        risk_amount = abs(entry - stop_loss)
        reward_1 = abs(take_profit_1 - entry)
        risk_reward_1 = f"1:{reward_1/risk_amount:.1f}" if risk_amount > 0 else "N/A"
        
        return {
            'signal': signal,
            'signal_icon': signal_icon,
            'confidence': confidence,
            'reasons': reasons,
            'entry': round(entry, 2),
            'stop_loss': round(stop_loss, 2),
            'take_profit_1': round(take_profit_1, 2),
            'take_profit_2': round(take_profit_2, 2),
            'take_profit_3': round(take_profit_3, 2),
            'risk_reward': risk_reward_1,
            'trend': trend,
            'momentum': momentum,
            'volatility': volatility,
            'pivots': pivots,
            'fibonacci': fib,
            'current_price': round(close, 2),
            'atr': round(atr, 2),
            'buy_score': buy_score,
            'sell_score': sell_score,
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
    
    def get_market_sentiment(self, df):
        """Calculate overall market sentiment."""
        if len(df) < 50:
            return {"sentiment": "غير محدد", "score": 50, "icon": "⚪"}
        
        # Calculate based on recent price action
        recent = df.tail(20)
        up_candles = len(recent[recent['close'] > recent['open']])
        down_candles = len(recent[recent['close'] < recent['open']])
        
        # Price momentum
        price_change_5 = (df.iloc[-1]['close'] - df.iloc[-5]['close']) / df.iloc[-5]['close'] * 100
        price_change_20 = (df.iloc[-1]['close'] - df.iloc[-20]['close']) / df.iloc[-20]['close'] * 100
        
        # Score calculation
        sentiment_score = 50
        sentiment_score += (up_candles - down_candles) * 2
        sentiment_score += price_change_5 * 3
        sentiment_score += price_change_20
        sentiment_score = max(0, min(100, sentiment_score))
        
        if sentiment_score >= 70:
            return {"sentiment": "تفاؤل قوي", "score": int(sentiment_score), "icon": "🤑", "color": "#00ff88"}
        elif sentiment_score >= 55:
            return {"sentiment": "تفاؤل", "score": int(sentiment_score), "icon": "😊", "color": "#90EE90"}
        elif sentiment_score <= 30:
            return {"sentiment": "تشاؤم قوي", "score": int(sentiment_score), "icon": "😰", "color": "#ff4444"}
        elif sentiment_score <= 45:
            return {"sentiment": "تشاؤم", "score": int(sentiment_score), "icon": "😟", "color": "#FFA500"}
        else:
            return {"sentiment": "محايد", "score": int(sentiment_score), "icon": "😐", "color": "#FFD700"}
    
    def get_full_analysis(self, df):
        """Get complete institutional-grade gold analysis."""
        if df is None or len(df) < 200:
            return None
        
        recommendation = self.generate_professional_recommendation(df)
        if not recommendation:
            return None
        
        sentiment = self.get_market_sentiment(df)
        
        return {
            'recommendation': recommendation,
            'sentiment': sentiment,
            'pivots': recommendation['pivots'],
            'fibonacci': recommendation['fibonacci'],
            'volatility': recommendation['volatility'],
            'trend': recommendation['trend'],
            'momentum': recommendation['momentum'],
            'timestamp': datetime.now().strftime('%H:%M:%S')
        }
