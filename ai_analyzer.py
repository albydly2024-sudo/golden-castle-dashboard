# AI Analyzer - Simplified Version
import pandas as pd
import numpy as np

class AIAnalyzer:
    def __init__(self):
        pass
        
    def detect_chart_patterns(self, df):
        if len(df) < 20:
            return {"pattern": "غير كافي", "confidence": 0, "signal": "NEUTRAL"}
        
        return {"pattern": "لا يوجد", "signal": "NEUTRAL", "confidence": 0}
    
    def get_news_sentiment(self, symbol="BTC"):
        sentiments = {
            "BTC": {"score": 55, "label": "محايد إيجابي"},
            "ETH": {"score": 60, "label": "إيجابي"},
            "PAXG": {"score": 50, "label": "محايد"}
        }
        return sentiments.get(symbol.split('/')[0], {"score": 50, "label": "محايد"})
    
    def predict_trend(self, df):
        if len(df) < 50:
            return "NEUTRAL"
        
        if 'RSI' not in df.columns or 'MACD' not in df.columns:
            return "NEUTRAL"
        
        latest_rsi = df['RSI'].iloc[-1] if not pd.isna(df['RSI'].iloc[-1]) else 50
        latest_macd = df['MACD'].iloc[-1] if not pd.isna(df['MACD'].iloc[-1]) else 0
        
        bullish_score = 0
        if latest_rsi < 40:
            bullish_score += 1
        if latest_macd > 0:
            bullish_score += 1
        
        if bullish_score >= 2:
            return "UP"
        elif bullish_score == 0:
            return "DOWN"
        else:
            return "NEUTRAL"
    
    def get_ai_score(self, df):
        pattern = self.detect_chart_patterns(df)
        trend = self.predict_trend(df)
        sentiment = self.get_news_sentiment()
        
        score = 50
        
        if pattern['signal'] == 'BUY':
            score += pattern['confidence'] * 0.3
        elif pattern['signal'] == 'SELL':
            score -= pattern['confidence'] * 0.3
        
        if trend == 'UP':
            score += 15
        elif trend == 'DOWN':
            score -= 15
        
        score += (sentiment['score'] - 50) * 0.2
        score = max(0, min(100, score))
        
        return {
            'score': round(score, 1),
            'pattern': pattern['pattern'],
            'trend': trend,
            'sentiment': sentiment['label']
        }
