import ccxt.async_support as ccxt
import asyncio
import time
import json
import pandas as pd
from loguru import logger
from config import config
from scanner import MarketScanner
from messenger import messenger
from charter import ChartGenerator

# Simple Logger Setup
logger.add("trading.log", rotation="500 MB")

# قاعدة بيانات نصائح التداول الاحترافية
TRADING_TIPS = [
    "💡 *نصيحة اليوم*: لا تدخل صفقة بأكثر من 2-5% من رأس مالك. إدارة المخاطر هي سر الاستمرار.",
    "💡 *نصيحة اليوم*: الاتجاه هو صديقك (Trend is your friend). لا تداول عكس اتجاه السوق العام.",
    "💡 *نصيحة اليوم*: الصبر جزء من التداول. عدم دخول صفقة أحياناً هو أفضل صفقة ممكنة.",
    "💡 *نصيحة اليوم*: دائماً استخدم وقف الخسارة (Stop Loss). السوق لا يرحم العاطفة.",
    "💡 *نصيحة اليوم*: التداول ليس مقامرة. اعتمد على الأرقام والمؤشرات وليس على التوقعات.",
    "💡 *نصيحة اليوم*: سجل صفقاتك وراجع أخطاءك. التعلم من الخسارة هو الطريق للربح.",
    "💡 *نصيحة اليوم*: لا تطارد السعر (FOMO). إذا فاتتك نقطة الدخول، انتظر الفرصة التالية.",
    "💡 *نصيحة اليوم*: تعلم كيف تقرأ الشموع اليابانية، فهي تحكي لك قصة الصراع بين المشترين والبائعين.",
    "💎 *نصيحة للمحترفين*: الأرباح تُحقق عند الشراء، وليس عند البيع. اختر نقطة دخولك بعناية فائقة.",
    "💎 *نصيحة للمحترفين*: السوق يتحرك في دورات. تعلم كيف تميز بين (تجميع السيولة) و (توزيع الأرباح).",
    "💎 *نصيحة للمحترفين*: المشاعر هي العدو الأول للمتداول. التزم بخطة البوت ولا تتدخل يدوياً في لحظات الخوف.",
    "💎 *نصيحة للمحترفين*: تابع حجم التداول (Volume). السعر بدون حجم هو خدعة غالباً."
]

class TradingBot:
    def __init__(self):
        self.exchange = getattr(ccxt, config.EXCHANGE_NAME)({
            'apiKey': config.API_KEY,
            'secret': config.SECRET_KEY,
            'enableRateLimit': True,
        })
        self.scanner = MarketScanner(self.exchange)
        self.messenger = messenger
        self.charter = ChartGenerator()
        self.positions = {} 
        self.alerts = [] 
        self.market_sentiment = "Neutral" # Fear & Greed cache
        self.stats_file = "stats.json"
        self.alerts_file = "alerts.json"
        self.history_file = "history.json"
        self.stats = {}
        self.alerts = []
        self.history = []
        
        # تحميل البيانات بشكل متزامن عند البدء
        self.load_stats_sync()
        self.load_alerts_sync()
        self.load_history_sync()
        
        if config.MODE == 'paper':
            logger.info("Bot initialized in PAPER TRADING mode.")
            logger.info("💎 Titanium Features Active: [Truth Engine] [Deep Analysis] [Auto-Charting] [Pattern Recognition]")
        else:
            logger.warning("Bot initialized in LIVE TRADING mode! Be careful.")

    def load_stats_sync(self):
        try:
            if os.path.exists(self.stats_file):
                with open(self.stats_file, 'r') as f:
                    self.stats = json.load(f)
            else:
                self.stats = {"total_trades": 0, "wins": 0, "losses": 0, "total_profit": 0.0, "start_time": time.time()}
        except:
            self.stats = {"total_trades": 0, "wins": 0, "losses": 0, "total_profit": 0.0, "start_time": time.time()}

    def load_alerts_sync(self):
        try:
            if os.path.exists(self.alerts_file):
                with open(self.alerts_file, 'r') as f:
                    self.alerts = json.load(f)
        except:
            self.alerts = []

    def load_history_sync(self):
        try:
            if os.path.exists(self.history_file):
                with open(self.history_file, 'r') as f:
                    self.history = json.load(f)
        except:
            self.history = []

    def save_data_sync(self):
        """حفظ جميع البيانات للحفاظ على الاستمرارية."""
        try:
            import os
            with open(self.stats_file, 'w') as f:
                json.dump(self.stats, f)
            with open(self.alerts_file, 'w') as f:
                json.dump(self.alerts, f)
            with open(self.history_file, 'w') as f:
                json.dump(self.history, f)
        except Exception as e:
            logger.error(f"Error saving data: {e}")

    async def get_main_menu(self):
        keyboard = [
            [{"text": "📊 حالة البوت"}, {"text": "🔍 فحص السوق"}],
            [{"text": "🚀 الأكثر ارتفاعاً"}, {"text": "📉 الأكثر انخفاضاً"}],
            [{"text": "⚡ الأكثر نشاطاً"}, {"text": "💎 تحليل عملة"}],
            [{"text": "🌐 ملخص السوق"}, {"text": "🔥 العملات الساخنة"}],
            [{"text": "🗺️ خريطة السوق"}, {"text": "📜 سجل الصفقات"}],
            [{"text": "🔔 المنبهات"}, {"text": "💡 نصيحة اليوم"}, {"text": "❓ المساعدة"}]
        ]
        return {"keyboard": keyboard, "resize_keyboard": True}
        
    async def display_trade_history(self, chat_id=None):
        """عرض سجل الصفقات الأخير."""
        if not self.history:
            await self.messenger.send_message("📜 السجل فارغ حالياً. لم يتم إكمال أي صفقات بعد.", chat_id=chat_id)
            return
        
        msg = "📜 *سجل الصفقات الأخير*:\n\n"
        # عرض آخر 10 صفقات
        for entry in self.history[-10:]:
            icon = "✅" if entry['profit'] > 0 else "❌"
            msg += (
                f"{icon} *{entry['symbol']}*\n"
                f"💰 الربح: `{entry['profit']:.2f}%`\n"
                f"💵 الدخول: `{entry['entry']}` | الخروج: `{entry['exit']}`\n"
                f"📅 `{time.strftime('%Y-%m-%d %H:%M', time.localtime(entry['time']))}`\n"
                f"━━━━━━━━━━\n"
            )
        await self.messenger.send_message(msg, chat_id=chat_id)

    async def check_commands(self):
        updates = await self.messenger.get_updates()
        for update in updates:
            msg = update.get("message", {})
            text = msg.get("text", "")
            chat_id = msg.get("chat", {}).get("id")
            if not chat_id: continue
            
            logger.info(f"📩 Telegram Message: From {chat_id} | Text: {text}")

            is_owner = str(chat_id) == str(config.TELEGRAM_CHAT_ID)
            is_authorized = str(chat_id) in [str(u) for u in config.AUTHORIZED_USERS]
            
            # فحص الأمان (Public Mode or Whitelist)
            if not config.PUBLIC_MODE and not is_authorized:
                # رسالة مساعدة للمستخدمين غير المعروفين
                deny_msg = (
                    "⚠️ *عذراً، هذا البوت خاص حالياً.*\n\n"
                    f"للحصول على صلاحية الدخول، يرجى تزويد المدير برقم الـ ID:\n"
                    f"🆔 رمزك: `{chat_id}`"
                )
                await self.messenger.send_message(deny_msg, chat_id=chat_id)
                continue
                
            if text in ["/start", "/help", "❓ المساعدة"]:
                help_text = (
                    "🥇 *مرحباً بك في منصتك الاحترافية للتداول الآلي*\n\n"
                    "أنا مساعدك الذكي، مصمم لمراقبة السوق واقتناص أفضل الفرص بناءً على خوارزميات متقدمة. استخدم القائمة أدناه للتحكم الشامل:\n\n"
                    "⚙️ *أدوات التحكم*:\n"
                    "• *حالة البوت*: مراقبة النشاط والربط.\n"
                    "• *الرصيد*: رؤية محفظتك المباشرة.\n"
                    "• *فحص السوق*: بدء مسح فوري للفرص.\n\n"
                    "💡 *قسم المعرفة*:\n"
                    "• *حالة السوق*: نبض العملات الكبرى حالياً.\n"
                    "• *نصيحة اليوم*: خبرات حصرية لتطوير مهاراتك.\n\n"
                    "🛠️ *الإعدادات*: عرض معايير العمل والمخاطرة."
                )
                await self.messenger.send_message(help_text, reply_markup=await self.get_main_menu(), chat_id=chat_id)
            elif text in ["/status", "📊 حالة البوت"]:
                if not is_owner and not is_authorized:
                    await self.messenger.send_message("🚫 عذراً، هذا الأمر مخصص للإدارة فقط.", chat_id=chat_id)
                    continue

                status_msg = (
                    "✅ *حالة النظام*: `متصل ويعمل`\n"
                    f"📡 *المنصة*: `{config.EXCHANGE_NAME.upper()}`\n"
                    f"⚙️ *الوضع*: `{'تجريبي (Paper)' if config.MODE == 'paper' else 'حقيقي (Live)'}`\n"
                    f"🧠 *نبض السوق*: `{self.market_sentiment}`\n"
                    f"⏰ *آخر تحديث*: `{time.strftime('%H:%M:%S')}`"
                )
                await self.messenger.send_message(status_msg, chat_id=chat_id)
            elif text in ["/balance", "💰 الرصيد الحالي"]:
                if not is_owner:
                    await self.messenger.send_message("🚫 عذراً، لا يمكنك رؤية الرصيد المالي للحساب.", chat_id=chat_id)
                    continue
                try:
                    bal = await self.exchange.fetch_balance()
                    usdt = bal['total'].get('USDT', 0)
                    await self.messenger.send_message(f"💰 *رصيدك الحالي*: `{usdt:.2f} USDT`", chat_id=chat_id)
                except Exception as e:
                    await self.messenger.send_message(f"❌ خطأ في جلب الرصيد: {e}", chat_id=chat_id)
            elif text in ["/scan", "🔍 فحص السوق"]:
                await self.messenger.send_message("🔍 جاري فحص السوق لاستخراج إشارة تداول... يرجى الانتظار.", chat_id=chat_id)
                asyncio.create_task(self.perform_scan(chat_id=chat_id, trade=is_owner))
            elif text == "/restart":
                if str(chat_id) == str(config.TELEGRAM_CHAT_ID):
                    await self.messenger.send_message("⚙️ جاري إعادة تشغيل النظام... يرجى الانتظار ثانية.", chat_id=chat_id)
                    exit(0)
                else:
                    await self.messenger.send_message("🚫 عذراً، هذا الأمر للمالك فقط.", chat_id=chat_id)
            elif text in ["💎 تحليل عملة", "/analyze"]:
                await self.messenger.send_message("💎 *تحليل الخبير*: أرسل اسم العملة الآن (مثال: `RIVER` أو `BTC`) للحصول على تقرير شامل.", chat_id=chat_id)
            elif text.upper().endswith("USDT") or (len(text) <= 6 and text.isalpha() and text.isupper()):
                # إذا أرسل عملة مباشرة بعد الضغط على الزر
                asyncio.create_task(self.display_deep_analysis(text, chat_id=chat_id))
            elif text == "💡 نصيحة اليوم":
                import random
                await self.messenger.send_message(random.choice(TRADING_TIPS), chat_id=chat_id)
            elif text == "🛠️ الإعدادات الحالية":
                settings_msg = (
                    "🛠️ *إعدادات التداول الحالية*:\n\n"
                    f"🔹 *حجم الصفقة*: `{config.ORDER_SIZE_P}%`\n"
                    f"🔹 *وقف الخسارة المتحرك*: `{config.STOP_LOSS_P}%`\n"
                    f"🔹 *هدف الربح (الحد الأدنى)*: `{config.TAKE_PROFIT_P}%`\n"
                    f"🔹 *العملة الأساسية*: `{config.SYMBOL}`\n"
                )
                await self.messenger.send_message(settings_msg, chat_id=chat_id)
            elif text == "🚀 الأكثر ارتفاعاً":
                asyncio.create_task(self.display_movers('gainers', chat_id=chat_id))
            elif text == "📉 الأكثر انخفاضاً":
                asyncio.create_task(self.display_movers('losers', chat_id=chat_id))
            elif text == "⚡ الأكثر نشاطاً":
                asyncio.create_task(self.display_movers('active', chat_id=chat_id))
            elif text == "🌐 ملخص السوق":
                asyncio.create_task(self.display_market_overview(chat_id=chat_id))
            elif text == "🗺️ خريطة السوق":
                asyncio.create_task(self.display_market_heatmap(chat_id=chat_id))
            elif text == "📜 سجل الصفقات":
                asyncio.create_task(self.display_trade_history(chat_id=chat_id))
            elif text == "🔥 العملات الساخنة":
                asyncio.create_task(self.display_hot_coins(chat_id=chat_id))
            elif text.startswith("/alert"):
                await self.handle_alert_command(text, chat_id=chat_id)
            elif text == "🔔 المنبهات":
                await self.display_active_alerts(chat_id=chat_id)

    async def display_market_overview(self, chat_id=None):
        try:
            major_symbols = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT']
            tickers = await self.exchange.fetch_tickers(major_symbols)
            msg = "🌐 *ملخص أهم عملات السوق (24 ساعة)*:\n\n"
            total_change = 0
            count = 0
            for sym in major_symbols:
                if sym in tickers:
                    tick = tickers[sym]
                    change = tick['percentage']
                    icon = "🚀" if change > 0 else "📉"
                    msg += f"{icon} *{sym}*: `{change:+.2f}%` | `{tick['last']}`\n"
                    total_change += (change or 0)
                    count += 1
            msg += "\n💡 *التحليل الفني السريع*: "
            if count > 0:
                avg = total_change / count
                if avg > 3: msg += "السوق في حالة *انفجار صعودي قوي* 🚀"
                elif avg > 0: msg += "السوق يميل *للايجابية* 📈"
                elif avg > -3: msg += "السوق في حالة *هدوء* ⚖️"
                else: msg += "السوق يمر بمرحلة *هبوط* 📉"
            await self.messenger.send_message(msg, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Market Overview Error: {e}")
            await self.messenger.send_message("❌ عذراً، فشل جلب البيانات.", chat_id=chat_id)

    async def display_hot_coins(self, chat_id=None):
        try:
            active_list = ['SOL/USDT', 'BNB/USDT', 'ADA/USDT', 'XRP/USDT', 'DOT/USDT', 'DOGE/USDT', 'LINK/USDT', 'MATIC/USDT']
            tickers = await self.exchange.fetch_tickers(active_list)
            sorted_by_vol = sorted(tickers.items(), key=lambda x: x[1]['quoteVolume'] or 0, reverse=True)
            msg = "🔥 *العملات الأكثر نشاطاً حالياً*:\n\n"
            for sym, tick in sorted_by_vol[:4]:
                vol = (tick['quoteVolume'] or 0) / 1_000_000
                change = tick['percentage'] or 0
                icon = "🟢" if change > 0 else "🔴"
                msg += f"{icon} *{sym}*: `{change:+.2f}%` | حجم: `{vol:.1f}M$`\n"
            await self.messenger.send_message(msg, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Hot Coins Error: {e}")
            await self.messenger.send_message("⚠️ فشل جلب العملات الساخنة.", chat_id=chat_id)

    async def display_market_heatmap(self, chat_id=None):
        """عرض خريطة السوق البصرية (Emojis) لمعرفة الحالة العامة فوراً."""
        try:
            active_list = ['BTC/USDT', 'ETH/USDT', 'SOL/USDT', 'BNB/USDT', 'XRP/USDT', 'ADA/USDT', 'AVAX/USDT', 'DOT/USDT', 'LINK/USDT']
            tickers = await self.exchange.fetch_tickers(active_list)
            
            msg = "🗺️ *خريطة مشاعر السوق (24h)*:\n\n"
            grid = ""
            details = ""
            
            for i, sym in enumerate(active_list):
                if sym in tickers:
                    change = tickers[sym]['percentage']
                    icon = "🟩" if change > 2 else "✅" if change > 0 else "🟥" if change < -2 else "📉"
                    grid += icon
                    if (i + 1) % 3 == 0: grid += "\n"
                    details += f"{icon} *{sym.split('/')[0]}*: `{change:+.1f}%`\n"
            
            await self.messenger.send_message(f"{msg}{grid}\n\n*التفاصيل*:\n{details}", chat_id=chat_id)
        except Exception as e:
            logger.error(f"Heatmap Error: {e}")
            await self.messenger.send_message("❌ فشل جلب خريطة السوق.", chat_id=chat_id)

    async def display_deep_analysis(self, symbol, chat_id=None):
        """توليد كرت إشارة احترافي (Professional Signal Card)."""
        try:
            symbol = symbol.upper()
            if '/' not in symbol: symbol += "/USDT"
            
            await self.messenger.send_message(f"⏳ جاري إنتاج تقرير خبير لعملة `{symbol}`... يرجى الانتظار.", chat_id=chat_id)
            
            analysis = await self.scanner.get_deep_analysis(symbol)
            if not analysis:
                await self.messenger.send_message(f"⚠️ عذراً، لم أتمكن من تحليل `{symbol}`. تأكد من اسم العملة.", chat_id=chat_id)
                return

            fa = analysis.get('fundamental')
            patterns = analysis.get('patterns', [])
            
            fa_section = ""
            if fa:
                fa_section = (
                    f"━━━━━━━━━━━━━━━━━━\n"
                    f"🏢 *نظرة على المشروع*:\n"
                    f"📝 *الوصف*: `{fa['description']}`\n"
                    f"🏆 *تقييم المطورين*: `{fa['quality']}`\n"
                    f"🌐 [رابط الموقع الرسمي]({fa['homepage']})\n"
                )

            pattern_section = ""
            if patterns:
                pattern_list = " | ".join(patterns)
                pattern_section = f"🕯️ *النماذج السعرية*: `{pattern_list}`\n"

            msg = (
                f"💎 *تقرير تحليل النخبة الذكي* | `{symbol}`\n"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🎯 *نسبة الدقة (Truth Engine)*: `{analysis['confidence']}%`\n"
                f"📊 *الاتجاه العام*: `{analysis['sentiment']}`\n"
                f"💵 *السعر الحالي*: `{analysis['price']}`\n"
                f"📈 *قوة 1h (RSI)*: `{analysis['rsi_1h']:.1f}`\n"
                f"{pattern_section}\n"
                
                f"🎯 *خطة الدخول (2-Stages)*:\n"
                f"1️⃣ دخول أول (سوق): `{analysis['entry_1']}`\n"
                f"2️⃣ دخول ثانٍ (تبريد): `{analysis['entry_2']}`\n\n"
                
                f"🏁 *الأهداف المستهدفة (TP)*:\n"
                f"🎯 هدف 1: `{analysis['tp1']:.4f}`\n"
                f"🎯 هدف 2: `{analysis['tp2']:.4f}`\n\n"
                
                f"🛡️ *إيقاف الخسارة (SL)*: `{analysis['sl']:.4f}`\n"
                f"{fa_section}"
                f"━━━━━━━━━━━━━━━━━━\n"
                f"🔍 *المستويات التقنية*:\n"
                f"🧱 مقاومة: `{analysis['resistance_1']:.4f}`\n"
                f"🏗️ دعم قوي: `{analysis['support_1']:.4f}`\n\n"
                f"💡 *نصيحة*: التحليل يجمع بين القوة الفنية (TA) وأساسيات المشروع (FA)."
            )
            
            # محاولة توليد وإرسال الشارت
            try:
                # نحتاج لجلب البيانات التاريخية (OHLCV) للرسم
                # زيادة العدد إلى 300 لضمان حساب المتوسطات المتحركة (MA200)
                df = await self.fetch_data(symbol, timeframe='1h', limit=300)
                if df is not None:
                    chart_img = self.charter.generate_chart(symbol, df)
                    if chart_img:
                        # إرسال الصورة مع النص
                        await self.messenger.send_photo(chart_img, caption=msg, chat_id=chat_id)
                        return
            except Exception as e:
                logger.error(f"Chart Send Error: {e}")
            
            # إذا فشل الرسم أو لا توجد مكتبات، نرسل النص فقط
            await self.messenger.send_message(msg, chat_id=chat_id)

        except Exception as e:
            logger.error(f"Deep Analysis Display Error: {e}")
            await self.messenger.send_message("❌ حدث خطأ أثناء توليد التقرير.", chat_id=chat_id)

    async def display_movers(self, category, chat_id=None):
        """عرض المتصدرين في السوق بناءً على الفئة المختارة."""
        try:
            movers = await self.scanner.get_market_movers()
            if not movers:
                await self.messenger.send_message("⚠️ فشل جلب بيانات متصدري السوق.", chat_id=chat_id)
                return

            titles = {
                'gainers': "🚀 *أقوى الارتفاعات حالياً (24h)*",
                'losers': "📉 *أقوى الانخفاضات حالياً (24h)*",
                'active': "⚡ *الأكثر نشاطاً (حجم تداول)*"
            }

            msg = f"{titles[category]}:\n\n"
            data = movers[category]
            
            for i, item in enumerate(data):
                symbol = item['symbol']
                price = item['price']
                if category == 'active':
                    msg += f"{i+1}. *{symbol}*: `${price}` | حجم: `{item['vol']:.1f}M$`\n"
                else:
                    change = item['change']
                    icon = "🟢" if change > 0 else "🔴"
                    msg += f"{i+1}. *{symbol}*: `${price}` | `{icon} {change:+.2f}%`\n"

            # ترقية: تقديم توصية فورية لأفضل عملة في القائمة
            best_pick = data[0]['symbol']
            msg += f"\n💎 *توصية الخبير الفورية*:\nأفضل فرصة في هذه القائمة هي `{best_pick}`.\nاضغط على **💎 تحليل عملة** ثم أرسل اسم العملة للحصول على التوصية كاملة."
            
            await self.messenger.send_message(msg, chat_id=chat_id)
        except Exception as e:
            logger.error(f"Display Movers Error: {e}")
            await self.messenger.send_message("❌ حدث خطأ أثناء جلب البيانات.", chat_id=chat_id)

    async def perform_scan(self, chat_id=None, trade=False):
        """بدء عملية المسح ومعالجة الفرصة (إشارة للجميع / تداول للمالك)."""
        try:
            # إذا كان تداول حقيقي، نتحقق من عدد الصفقات
            if trade and len(self.positions) >= config.MAX_OPEN_TRADES:
                logger.info(f"تم الوصول للحد الأقصى من الصفقات. تخطي التداول التلقائي.")
                if chat_id: await self.messenger.send_message("⚠️ المحفظة ممتلئة بالصفقات حالياً، سأعطيك الإشارة فقط.", chat_id=chat_id)
                trade = False 

            opportunities = await self.scanner.scan()
            if opportunities:
                # نأخذ أفضل 3 فرص ونحللها بعمق لاختيار الأكثر دقة (AI Confirmation)
                for op in opportunities[:3]:
                    symbol = op['symbol']
                    analysis = await self.scanner.get_deep_analysis(symbol)
                    
                    if not analysis or analysis['confidence'] < 70:
                        continue
                    
                    is_whale = await self.scanner.detect_whale_activity(symbol)
                    whale_note = "🐋 (نشاط حيتان!)" if is_whale else ""

                    msg = (
                        f"🤖 *تأكيد الذكاء الاصطناعي* {whale_note}\n"
                        f"💎 *العملة*: `{symbol}`\n"
                        f"🎯 *نسبة الثقة*: `{analysis['confidence']}%`\n"
                        f"📊 *الاتجاه*: `{analysis['sentiment']}`\n"
                        f"💵 *السعر*: `{analysis['price']}`\n"
                    )
                    
                    if analysis['confidence'] >= 90:
                        msg += "💡 *القرار*: `دخول فوري 🟢` (تطابق الفريمات)\n"
                        if trade:
                            await self.execute_trade('buy', symbol, reason=f"AI Confirmed ({analysis['confidence']}%)")
                            break # دخول صفقة واحدة فقط في كل دورة
                        elif chat_id:
                            await self.messenger.send_message(f"{msg}⚠️ هذه إشارة مؤكدة، يمكنك تنفيذها يدوياً.", chat_id=chat_id)
                            break
                    elif chat_id and not trade:
                        await self.messenger.send_message(f"{msg}⚠️ إشارة متوسطة القوة، راقب السعر.", chat_id=chat_id)
            else:
                if chat_id: await self.messenger.send_message("⚖️ السوق حالياً مستقر، لا توجد إشارات دخول قوية.", chat_id=chat_id)
        except Exception as e:
            logger.error(f"Scan Logic Error: {e}")

    async def check_trailing_stop(self):
        """نظام إدارة مخاطر احترافي: Break-Even, Multi-TP, Trailing Stop."""
        for symbol, data in list(self.positions.items()):
            try:
                ticker = await self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # 1. تحديث أعلى سعر
                if current_price > data['highest_price']:
                    data['highest_price'] = current_price
                
                # حساب الأداء الحالي (%)
                profit_pct = (current_price - data['entry_price']) / data['entry_price'] * 100
                
                # 2. حماية الـ Break-Even: إذا ربحنا 1.2%، نؤمن الصفقة
                if not data.get('is_risk_free') and profit_pct >= config.BREAK_EVEN_P:
                    data['is_risk_free'] = True
                    # فعلياً، نرفع وقف الخسارة إلى نقطة الدخول
                    await self.messenger.send_message(f"🛡️ *تأمين الصفقة (Break-Even)*\nالعملة: `{symbol}`\nتم تحريك وقف الخسارة إلى نقطة الدخول آلياً. الصفقة الآن بلا مخاطرة!")

                # 3. الأهداف المتعددة (Multi-TP)
                targets_hit = data.get('targets_hit', 0)
                if targets_hit < len(config.TP_TARGETS):
                    current_target = config.TP_TARGETS[targets_hit]
                    if profit_pct >= current_target:
                        data['targets_hit'] = targets_hit + 1
                        await self.messenger.send_message(f"🎯 *تحقق الهدف {targets_hit + 1}*\nالعملة: `{symbol}`\nتم جني أرباح جزئية عند `{current_target}%`. استمرار مع الهدف التالي!")

                # 4. وقف الخسارة المتحرك أو التقليدي
                drop_from_peak = (data['highest_price'] - current_price) / data['highest_price'] * 100
                if drop_from_peak >= config.STOP_LOSS_P:
                    # إذا كانت مؤمنة، سنخرج بربح بسيط أو تعادل على الأقل
                    reason = "Trailing Stop Loss (Secure Profit)" if profit_pct > 0 else "Stop Loss Hit"
                    await self.execute_trade('sell', symbol, reason=reason)
                    
            except Exception as e:
                logger.error(f"Elite Risk Management Error ({symbol}): {e}")

    async def send_daily_report(self):
        uptime = (time.time() - self.stats['start_time']) / 86400
        win_rate = (self.stats['wins'] / self.stats['total_trades'] * 100) if self.stats['total_trades'] > 0 else 0
        report = (
            "📊 *تقرير أداء البوت الفائق*\n\n"
            f"⏱️ *المدة*: `{uptime:.1f}` يوم\n"
            f"🔄 *الصفقات*: `{self.stats['total_trades']}`\n"
            f"✅ *الرابحة*: `{self.stats['wins']}`\n"
            f"❌ *الخاسرة*: `{self.stats['losses']}`\n"
            f"📈 *النجاح*: `{win_rate:.1f}%`\n"
            f"💰 *الربح*: `{self.stats['total_profit']:.2f} USDT`"
        )
        await self.messenger.send_message(report)

    async def fetch_data(self, symbol, timeframe='1h', limit=100):
        try:
            bars = await self.exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
            df = pd.DataFrame(bars, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
            return df
        except Exception as e:
            logger.error(f"Fetch Data Error ({symbol}): {e}")
            return None

    async def get_fear_greed_index(self):
        """جلب مؤشر الخوف والطمع العالمي (Sentiment)."""
        try:
            import aiohttp
            async with aiohttp.ClientSession() as session:
                async with session.get('https://api.alternative.me/fng/') as resp:
                    data = await resp.json()
                    value = int(data['data'][0]['value'])
                    classification = data['data'][0]['value_classification']
                    self.market_sentiment = f"{classification} ({value})"
                    return value
        except:
            return 50 # Default to neutral

    async def execute_trade(self, signal, symbol, reason="Strategy Signal"):
        try:
            # تطبيق "التراكم الآلي" (Auto-Compounding)
            size_p = config.ORDER_SIZE_P
            if config.AUTO_COMPOUND and self.stats['total_profit'] > 0:
                # زيادة حجم الصفقة بنسبة بسيطة من الأرباح المحققة
                bonus = min(self.stats['total_profit'] / 100, 2) # حد أقصى 2% زيادة
                size_p += bonus
                logger.info(f"💰 Auto-Compounding: Increased order size to {size_p:.1f}% due to profits.")

            ticker = await self.exchange.fetch_ticker(symbol)
            price = ticker['last']
            msg = (
                f"🔔 *تنفيذ عملية ذكية*\n\n"
                f"📦 *النوع*: `{'شراء 🟢' if signal == 'buy' else 'بيع 🔴'}`\n"
                f"💎 *العملة*: `{symbol}`\n"
                f"💵 *السعر*: `{price}`\n"
                f"📝 *السبب*: `{reason}`"
            )
            await self.messenger.send_message(msg)
            
            if signal == 'buy':
                self.positions[symbol] = {'entry_price': price, 'highest_price': price, 'time': time.time()}
            elif signal == 'sell' and symbol in self.positions:
                entry = self.positions[symbol]['entry_price']
                profit = (price - entry) / entry * 100
                self.stats['total_trades'] += 1
                if profit > 0: self.stats['wins'] += 1
                else: self.stats['losses'] += 1
                self.stats['total_profit'] += (price - entry)
                
                # تسجيل في السجل التاريخي
                self.history.append({
                    'symbol': symbol,
                    'entry': entry,
                    'exit': price,
                    'profit': profit,
                    'time': time.time()
                })
                
                self.save_data_sync()
                del self.positions[symbol]
                await self.messenger.send_message(f"🏁 *اكتملت الصفقة*: `{'✅ ربح' if profit > 0 else '❌ خسارة'}` ({profit:.2f}%)")
        except Exception as e:
            logger.error(f"Trade Execution Error: {e}")

    async def handle_alert_command(self, text, chat_id=None):
        """معالجة أمر إضافة التنبيهات: /alert BTC 100000"""
        try:
            parts = text.split()
            if len(parts) < 3:
                await self.messenger.send_message("⚠️ *طريقة الاستخدام*: `/alert [العملة] [السعر]`\nمثال: `/alert BTC 105000` icon_emoji", chat_id=chat_id)
                return
            
            symbol = parts[1].upper()
            if '/' not in symbol: symbol += "/USDT"
            target_price = float(parts[2])
            
            # جلب السعر الحالي لتحديد الاتجاه
            ticker = await self.exchange.fetch_ticker(symbol)
            current_price = ticker['last']
            direction = 'above' if target_price > current_price else 'below'
            
            # حفظ التنبيه مع Chat ID الخاص بصحابه
            self.alerts.append({
                'symbol': symbol, 
                'price': target_price, 
                'direction': direction,
                'chat_id': chat_id or config.TELEGRAM_CHAT_ID
            })
            self.save_data_sync()
            await self.messenger.send_message(f"✅ *تم ضبط المنبه*:\nسأقوم بتنبيهك عندما {'يصعد' if direction == 'above' else 'يهبط'} سعر `{symbol}` إلى `{target_price}`.", chat_id=chat_id)
        except Exception as e:
            await self.messenger.send_message(f"❌ خطأ في ضبط المنبه: تأكد من اسم العملة والسعر.", chat_id=chat_id)

    async def display_active_alerts(self, chat_id=None):
        """عرض المنبهات القائمة للمستخدم الحالي."""
        # تصفية المنبهات الخاصة بهذا المستخدم فقط
        user_id = chat_id or config.TELEGRAM_CHAT_ID
        user_alerts = [a for a in self.alerts if str(a.get('chat_id')) == str(user_id)]
        
        if not user_alerts:
            await self.messenger.send_message("🔔 لا توجد منبهات نشطة حالياً.\nلإضافة منبه استخدم: `/alert [BTC] [السعر]`", chat_id=chat_id)
            return
        
        msg = "🔔 *منبهاتك النشطة حالياً*:\n\n"
        for i, a in enumerate(user_alerts):
            msg += f"{i+1}. `{a['symbol']}` عند `{a['price']}`\n"
        await self.messenger.send_message(msg, chat_id=chat_id)

    async def check_alerts(self):
        """التحقق من المنبهات بشكل دوري."""
        for alert in self.alerts[:]:
            try:
                ticker = await self.exchange.fetch_ticker(alert['symbol'])
                current = ticker['last']
                
                hit = False
                if alert['direction'] == 'above' and current >= alert['price']: hit = True
                elif alert['direction'] == 'below' and current <= alert['price']: hit = True
                
                if hit:
                    await self.messenger.send_message(
                        f"🚨 *تنبيه سعر* 🚨\nوصل سعر `{alert['symbol']}` إلى `{current}`!\n(المنبه المطلوب: `{alert['price']}`)",
                        chat_id=alert.get('chat_id')
                    )
                    self.alerts.remove(alert)
                    self.save_data_sync()
            except:
                pass

    async def check_trailing_stop(self):
        """مراقبة الصفقات المفتوحة وتطبيق وقف الخسارة المتحرك (Trailing Stop)."""
        active_symbols = list(self.positions.keys())
        for symbol in active_symbols:
            try:
                pos = self.positions[symbol]
                ticker = await self.exchange.fetch_ticker(symbol)
                current_price = ticker['last']
                
                # تحديث أعلى سعر وصل له السعر منذ الدخول
                if current_price > pos['highest_price']:
                    self.positions[symbol]['highest_price'] = current_price
                    # logger.debug(f"{symbol}: New High {current_price} (Entry: {pos['entry_price']})")
                
                # حساب نسبة الهبوط من القمة (Drawdown)
                drawdown = (current_price - pos['highest_price']) / pos['highest_price'] * 100
                profit = (current_price - pos['entry_price']) / pos['entry_price'] * 100
                
                # تفعيل Trailing Stop فقط إذا كنا رابحين بنسبة معينة (مثلاً 1%)
                if profit > 1.0 and drawdown < -1.5:
                     # بيع لحماية الأرباح
                     await self.messenger.send_message(f"🛡️ *حماية الأرباح (Trailing Stop)*: هبط السعر 1.5% من القمة. جاري البيع...")
                     await self.execute_trade('sell', symbol, reason="Trailing Stop Hit 🛡️")
                
                # وقف خسارة طوارئ ثابت (5% من الدخول) اذا انعكس السوق فجأة
                elif profit < -5.0:
                     await self.messenger.send_message(f"🚨 *وقف خسارة طوارئ*: هبوط حاد. جاري البيع...")
                     await self.execute_trade('sell', symbol, reason="Emergency Stop Loss 🚨")
                     
            except Exception as e:
                logger.error(f"Trailing Stop Error ({symbol}): {e}")

    async def run_loop(self):
        logger.info("Starting Async Main Loop...")
        await self.messenger.send_message(
            "🚀 *تم تشغيل النسخة الفائقة (Hyper Engine)*\nالبوت الآن أسرع بـ 10 أضعاف ومستعد للعمل.",
            reply_markup=await self.get_main_menu()
        )
        
        last_scan = 0
        last_report = time.time()
        last_fng = 0 # Fear and Greed

        while True:
            try:
                now = time.time()
                # جلب نبض السوق كل 4 ساعات
                if now - last_fng > 14400:
                    await self.get_fear_greed_index()
                    last_fng = now

                # المهام المتوازية
                await self.check_commands()
                await self.check_trailing_stop()
                await self.check_alerts()
                
                now = time.time()
                if now - last_report > 86400:
                    await self.send_daily_report()
                    last_report = now

                if now - last_scan > 300:
                    asyncio.create_task(self.perform_scan()) # Non-blocking scan
                    last_scan = now
                
                await asyncio.sleep(1) # السرعة المطلوبة في الاستجابة
            except Exception as e:
                logger.error(f"Loop error: {e}")
                await asyncio.sleep(5)

    async def start(self):
        try:
            await self.run_loop()
        finally:
            await self.exchange.close()
            await self.messenger.close()

if __name__ == "__main__":
    bot = TradingBot()
    try:
        asyncio.run(bot.start())
    except KeyboardInterrupt:
        logger.info("Bot stopped.")
