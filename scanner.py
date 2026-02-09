import ccxt.async_support as ccxt
import pandas as pd
import asyncio
import aiohttp
from loguru import logger
from config import config

class MarketScanner:
    def __init__(self, exchange):
        self.exchange = exchange
        self.project_cache = {}

    async def get_project_fundamental(self, symbol):
        """جلب بيانات المشروع الأساسية (الوصف، المطورين، الحماية)."""
        try:
            coin_id = symbol.split('/')[0].lower()
            if coin_id in self.project_cache: return self.project_cache[coin_id]

            url = f"https://api.coingecko.com/api/v3/coins/{coin_id}?localization=false&tickers=false&market_data=false&community_data=false&developer_data=true"
            async with aiohttp.ClientSession() as session:
                async with session.get(url, timeout=5) as resp:
                    if resp.status == 200:
                        data = await resp.json()
                        desc = data.get('description', {}).get('en', '').split('.')[0] # أول جملة
                        dev_score = data.get('developer_score', 0)
                        
                        # تقييم جودة المشروع
                        if dev_score > 70: quality = "مشرق ومستقر جداً 💎"
                        elif dev_score > 40: quality = "ناجح وواعد 🚀"
                        else: quality = "عالي المخاطرة (جديد) ⚠️"

                        info = {
                            'description': desc if desc else "لا يتوفر وصف حالياً لهذا المشروع.",
                            'score': dev_score,
                            'quality': quality,
                            'homepage': data.get('links', {}).get('homepage', [None])[0]
                        }
                        self.project_cache[coin_id] = info
                        return info
            return None
        except Exception as e:
            logger.debug(f"FA Error for {symbol}: {e}")
            return None

    async def detect_candle_patterns(self, df):
        """الكشف عن نماذج الشموع اليابانية (Price Action)."""
        try:
            current = df.iloc[-1]
            prev = df.iloc[-2]
            
            body = abs(current['close'] - current['open'])
            upper_shadow = current['high'] - max(current['close'], current['open'])
            lower_shadow = min(current['close'], current['open']) - current['low']
            
            patterns = []
            
            # 1. المطرقة (Hammer) - إشارة صعودية
            if lower_shadow > (body * 2) and upper_shadow < (body * 0.5):
                patterns.append("Hammer 🔨")
                
            # 2. الدوجي (Doji) - حيرة
            if body <= (current['close'] * 0.001):
                patterns.append("Doji ➕")
                
            # 3. الابتلاع (Engulfing)
            if current['close'] > prev['open'] and current['open'] < prev['close']:
                patterns.append("Bullish Engulfing 🟢")
            elif current['close'] < prev['open'] and current['open'] > prev['close']:
                patterns.append("Bearish Engulfing 🔴")
                
            return patterns
        except:
            return []

    async def detect_whale_activity(self, symbol):
        """رصد نشاط الحيتان عبر مراقبة انفجارات حجم التداول المفاجئة."""
        try:
            # جلب آخر 50 شمعة (دقيقة واحدة لسرعة الرصد)
            bars = await self.exchange.fetch_ohlcv(symbol, timeframe='1m', limit=50)
            if not bars: return False
            
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # حساب متوسط الحجم لآخر 50 دقيقة
            avg_volume = df['volume'].iloc[:-1].mean()
            current_volume = df['volume'].iloc[-1]
            
            # إذا كان الحجم الحالي أكبر من المتوسط بـ 3 أضعاف (Whale Multiplier)
            is_whale = current_volume > (avg_volume * config.WHALE_VOL_MULTIPLIER)
            
            if is_whale:
                logger.info(f"🐋 Whale detected on {symbol}! Volume: {current_volume:.2f} (Avg: {avg_volume:.2f})")
            
            return is_whale
        except:
            return False

    def calculate_atr(self, df, period=14):
        """حساب متوسط النطاق الحقيقي (ATR) لقياس التقلب."""
        try:
            high = df['high']
            low = df['low']
            close = df['close']
            prev_close = close.shift(1)
            
            tr1 = high - low
            tr2 = abs(high - prev_close)
            tr3 = abs(low - prev_close)
            
            tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
            atr = tr.rolling(window=period).mean()
            return atr
        except:
            return pd.Series([0] * len(df))

    def calculate_rsi(self, series, period=14):
        """Manual RSI calculation using Pandas."""
        delta = series.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def calculate_atr(self, df, period=14):
        """Manual ATR (Average True Range) calculation."""
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        ranges = pd.concat([high_low, high_close, low_close], axis=1)
        true_range = ranges.max(axis=1)
        return true_range.rolling(window=period).mean()

    async def get_top_symbols(self, quote_currency='USDT', limit=250):
        """جلب أفضل العملات بناءً على حجم التداول لضمان جودة الإشارات."""
        try:
            tickers = await self.exchange.fetch_tickers()
            # تصفية العملات التي تنتهي بـ USDT وترتيبها حسب الحجم
            symbols = [
                s for s, t in tickers.items() 
                if s.endswith(f'/{quote_currency}') and t['quoteVolume'] > 0
            ]
            symbols.sort(key=lambda x: tickers[x]['quoteVolume'], reverse=True)
            return symbols[:limit]
        except Exception as e:
            logger.error(f"Error fetching symbols: {e}")
            return []

    async def get_deep_analysis(self, symbol):
        """محرك الحقيقة (Truth Engine): تحليل متعدد الفريمات لضمان الدقة."""
        try:
            # جلب البيانات لثلاثة فريمات زمنية
            tasks = [
                self.exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50),
                self.exchange.fetch_ohlcv(symbol, timeframe='1h', limit=100),
                self.exchange.fetch_ohlcv(symbol, timeframe='4h', limit=50)
            ]
            results = await asyncio.gather(*tasks)
            
            if not all(results): return None
            
            df_15m = pd.DataFrame(results[0], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df_1h = pd.DataFrame(results[1], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df_4h = pd.DataFrame(results[2], columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            
            # حساب RSI لكل فريم
            rsi_15m = self.calculate_rsi(df_15m['close']).iloc[-1]
            rsi_1h = self.calculate_rsi(df_1h['close']).iloc[-1]
            rsi_4h = self.calculate_rsi(df_4h['close']).iloc[-1]
            
            last_price = df_1h['close'].iloc[-1]
            
            # حساب نقاط الارتكاز (Pivot Points) من فريم الساعة
            recent_24h = df_1h.iloc[-24:]
            high = recent_24h['high'].max()
            low = recent_24h['low'].min()
            close = recent_24h['close'].iloc[-1]
            pivot = (high + low + close) / 3
            r1, s1 = (2 * pivot) - low, (2 * pivot) - high
            r2, s2 = pivot + (high - low), pivot - (high - low)
            
            # حساب نماذج الشموع (Algorithmic Pattern Recognition)
            patterns = await self.detect_candle_patterns(df_1h)
            
            # حساب مؤشر التقلب (ATR) لإدارة المخاطر
            atr_series = self.calculate_atr(df_1h)
            current_atr = atr_series.iloc[-1]
            
            # تحديد وقف الخسارة وجني الأرباح ديناميكياً بناءً على التقلب
            # SL = 2 * ATR (لإعطاء مساحة للسعر للتنفس في الأسواق العنيفة)
            atr_sl = last_price - (2 * current_atr)
            
            # TP1 = 1.5 * ATR (هدف أول سريع)
            # TP2 = 4.0 * ATR (هدف استثماري بعيد)
            atr_tp1 = last_price + (1.5 * current_atr)
            atr_tp2 = last_price + (4.0 * current_atr)

            # حساب "نسبة الثقة" (Truth Score)
            # إذا اتفقت الفريمات الثلاثة على الاتجاه (فوق أو تحت الـ 50 في RSI)
            trend_15m = 1 if rsi_15m > 50 else -1
            trend_1h = 1 if rsi_1h > 50 else -1
            trend_4h = 1 if rsi_4h > 50 else -1
            
            agreement = (trend_15m + trend_1h + trend_4h)
            if agreement == 3: 
                sentiment = "صاعد قوي جداً 🚀🔥"
                confidence = 95
            elif agreement == -3:
                sentiment = "هابط قوي جداً 📉⚠️"
                confidence = 95
            elif agreement >= 1:
                sentiment = "إيجابي 📈"
                confidence = 70
            else:
                sentiment = "سلبي 📉"
                confidence = 70

            # جلب البيانات الأساسية للمشروع (Fundamental Analysis)
            fa_data = await self.get_project_fundamental(symbol)

            return {
                'symbol': symbol,
                'price': last_price,
                'rsi_1h': rsi_1h,
                'sentiment': sentiment,
                'confidence': confidence,
                'patterns': patterns, # نماذج الشموع
                'fundamental': fa_data,
                'entry_1': last_price,
                'entry_2': s1 if s1 < last_price else last_price * 0.98,
                'tp1': atr_tp1, # استخدام ATR
                'tp2': atr_tp2, # استخدام ATR
                'sl': atr_sl,   # استخدام ATR
                'support_1': s1, 'support_2': s2,
                'resistance_1': r1, 'resistance_2': r2
            }
        except Exception as e:
            logger.error(f"Deep Analysis Error for {symbol}: {e}")
            return None

    def calculate_macd(self, series, fast=12, slow=26, signal=9):
        """Manual MACD calculation."""
        exp1 = series.ewm(span=fast, adjust=False).mean()
        exp2 = series.ewm(span=slow, adjust=False).mean()
        macd = exp1 - exp2
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        return macd, signal_line

    async def analyze_symbol(self, symbol, timeframe='1h'):
        """رصد الفرص الأولية بناءً على المؤشرات القياسية."""
        try:
            bars = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=100)
            if not bars: return None
            
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            df['RSI'] = self.calculate_rsi(df['close'])
            df['EMA_20'] = df['close'].ewm(span=20, adjust=False).mean()
            
            last_price = df['close'].iloc[-1]
            last_rsi = df['RSI'].iloc[-1]
            last_ema = df['EMA_20'].iloc[-1]
            
            # حساب الزخم (Momentum)
            momentum = ((last_price - last_ema) / last_ema) * 100
            
            return {
                'symbol': symbol,
                'price': last_price,
                'rsi': last_rsi,
                'momentum': momentum
            }
        except Exception as e:
            logger.debug(f"Error analyzing {symbol}: {e}")
            return None

    async def get_market_movers(self, quote_currency='USDT', limit=5):
        """جلب المتصدرين مع تحليل سريع."""
        try:
            tickers = await self.exchange.fetch_tickers()
            usdt_tickers = {s: t for s, t in tickers.items() if s.endswith(f'/{quote_currency}') and t['quoteVolume'] > 0}
            
            gainers = sorted(usdt_tickers.items(), key=lambda x: x[1]['percentage'] or 0, reverse=True)[:limit]
            losers = sorted(usdt_tickers.items(), key=lambda x: x[1]['percentage'] or 0)[:limit]
            active = sorted(usdt_tickers.items(), key=lambda x: x[1]['quoteVolume'] or 0, reverse=True)[:limit]
            
            return {
                'gainers': [{'symbol': s, 'change': t['percentage'], 'price': t['last']} for s, t in gainers],
                'losers': [{'symbol': s, 'change': t['percentage'], 'price': t['last']} for s, t in losers],
                'active': [{'symbol': s, 'vol': (t['quoteVolume'] or 0)/1_000_000, 'price': t['last']} for s, t in active]
            }
        except Exception as e:
            logger.error(f"Movers Error: {e}")
            return None

    async def scan(self, quote_currency='USDT'):
        """مسح شامل وفائق السرعة لـ 250 عملة مع تأكيد ذكي."""
        logger.info(f"📡 جاري رصد الفرص في 250 عملة...")
        symbols = await self.get_top_symbols(quote_currency)
        
        sem = asyncio.Semaphore(15)
        
        async def bounded_analyze(symbol):
            async with sem:
                return await self.analyze_symbol(symbol)

        tasks = [bounded_analyze(s) for s in symbols]
        results = await asyncio.gather(*tasks)
        opportunities = [r for r in results if r is not None]
        
        # ترتيب الفرص حسب الزخم
        opportunities.sort(key=lambda x: x['momentum'], reverse=True)
        return opportunities
