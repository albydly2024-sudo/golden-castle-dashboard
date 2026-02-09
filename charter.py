import pandas as pd
import io
from loguru import logger

try:
    import mplfinance as mpf
    HAS_PLOT = True
except ImportError:
    HAS_PLOT = False
    logger.warning("mplfinance not found. Chart generation disabled.")

class ChartGenerator:
    def __init__(self):
        if HAS_PLOT:
            self.style = mpf.make_mpf_style(base_mpf_style='nightclouds', rc={'font.size':10})
        else:
            self.style = None

    def generate_chart(self, symbol, df):
        """توليد صورة احترافية للشموع اليابانية مع المؤشرات."""
        if not HAS_PLOT: return None
        try:
            # تجهيز البيانات
            df.index = pd.to_datetime(df['timestamp'], unit='ms')
            
            # مؤشرات فنية (Moving Averages)
            add_plots = []
            
            if len(df) > 50:
                ma50 = df['close'].rolling(window=50).mean()
                add_plots.append(mpf.make_addplot(ma50, color='cyan', width=1.5, label='MA 50'))
            
            if len(df) > 200:
                ma200 = df['close'].rolling(window=200).mean()
                add_plots.append(mpf.make_addplot(ma200, color='orange', width=1.5, label='MA 200'))
            
            # منع الرسم إذا لم تتوفر مؤشرات (لتفادي خطأ المصفوفة الفارغة)
            if not add_plots and len(df) < 50:
                 return None

            # إضافة أحجام التداول (Volume) والمؤشرات
            
            # حفظ الصورة في الذاكرة (Buffer)
            buf = io.BytesIO()
            mpf.plot(
                df,
                type='candle',
                style=self.style,
                volume=True,
                addplot=add_plots,
                title=f"\nElite Analysis: {symbol}",
                savefig=dict(fname=buf, dpi=100, pad_inches=0.25),
                tight_layout=True,
                figsize=(10, 6)
            )
            buf.seek(0)
            return buf
        except Exception as e:
            logger.error(f"Chart Generation Error ({symbol}): {e}")
            return None
