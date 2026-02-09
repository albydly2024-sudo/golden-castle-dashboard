"""
=======================================================
🏰 Golden Citadel - Institutional Trading Terminal
Phase 7: Premium Dashboard v2.0
=======================================================
"""

import streamlit as st
import pandas as pd
import time
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import database
import config
from market_data import BinanceClient
from strategy import Strategy
from gold_analyzer import GoldAnalyzer
from backtester import Backtester
from ai_analyzer import AIAnalyzer
from risk_manager import RiskManager

# ==========================================================
# 1. Page Configuration
# ==========================================================
st.set_page_config(
    page_title="القلعة الذهبية | Golden Citadel",
    page_icon="🏰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Load Premium CSS
with open('style.css', encoding="utf-8") as f:
    st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# ==========================================================
# 2. Initialize Components
# ==========================================================
@st.cache_resource
def get_bot_components():
    """Initialize Client and Strategy once."""
    return BinanceClient(), Strategy(), GoldAnalyzer(), AIAnalyzer(), Backtester(), RiskManager()

client, strategy, gold_analyzer, ai_analyzer, backtester, risk_manager = get_bot_components()

# ==========================================================
# 3. Advanced Charting Function
# ==========================================================
def create_professional_chart(df, symbol):
    """Creates institutional-grade trading chart with multiple indicators."""
    
    # Determine asset name for display (use Arabic labels)
    symbol_names = {
        'PAXG/USDT': '🥇 الذهب (PAXG)',
        'BTC/USDT': '₿ بيتكوين',
        'ETH/USDT': 'Ξ إيثريوم',
        'BNB/USDT': '🔶 بينانس',
        'SOL/USDT': '☀️ سولانا',
        'XRP/USDT': '💧 ريبل',
        'DOGE/USDT': '🐕 دوجكوين'
    }
    display_name = symbol_names.get(symbol, symbol)
    
    fig = make_subplots(
        rows=3, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.03,
        subplot_titles=(f'📊 {display_name}', '📉 مؤشر الماكد (MACD)', '📊 حجم التداول'),
        row_heights=[0.6, 0.2, 0.2]
    )

    # === Row 1: Candlestick + Bollinger + EMA ===
    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df['timestamp'],
        open=df['open'], high=df['high'],
        low=df['low'], close=df['close'],
        name='السعر',
        increasing_line_color='#00ff88',
        decreasing_line_color='#ff4444'
    ), row=1, col=1)

    # EMA 200
    if 'EMA_200' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['EMA_200'],
            line=dict(color='#FFD700', width=2, dash='dot'),
            name='متوسط 200 يوم'
        ), row=1, col=1)

    # Bollinger Bands
    if 'BBU_20_2.0' in df.columns:
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['BBU_20_2.0'],
            line=dict(color='rgba(0, 212, 255, 0.5)', width=1),
            name='بولنجر العلوي'
        ), row=1, col=1)
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['BBL_20_2.0'],
            line=dict(color='rgba(0, 212, 255, 0.5)', width=1),
            fill='tonexty', fillcolor='rgba(0, 212, 255, 0.05)',
            name='بولنجر السفلي'
        ), row=1, col=1)

    # === Row 2: MACD ===
    if 'MACD' in df.columns:
        # Histogram with color coding
        colors = ['#00ff88' if val >= 0 else '#ff4444' for val in df['MACD_Hist']]
        fig.add_trace(go.Bar(
            x=df['timestamp'], y=df['MACD_Hist'],
            marker_color=colors, opacity=0.7,
            name='الهيستوجرام'
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MACD'],
            line=dict(color='#00d4ff', width=2),
            name='خط الماكد'
        ), row=2, col=1)
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], y=df['MACD_Signal'],
            line=dict(color='#FFD700', width=2),
            name='خط الإشارة'
        ), row=2, col=1)

    # === Row 3: Volume ===
    if 'volume' in df.columns:
        vol_colors = ['#00ff88' if df.iloc[i]['close'] >= df.iloc[i]['open'] else '#ff4444' 
                     for i in range(len(df))]
        fig.add_trace(go.Bar(
            x=df['timestamp'], y=df['volume'],
            marker_color=vol_colors, opacity=0.6,
            name='الحجم'
        ), row=3, col=1)

    # === Layout ===
    fig.update_layout(
        template='plotly_dark',
        height=700,
        margin=dict(l=10, r=10, t=50, b=10),
        xaxis_rangeslider_visible=False,
        font=dict(family="Cairo, Poppins, sans-serif", size=12),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,10,10,0.9)'
    )
    
    # Grid styling
    fig.update_xaxes(gridcolor='rgba(255,255,255,0.05)', showgrid=True)
    fig.update_yaxes(gridcolor='rgba(255,255,255,0.05)', showgrid=True)
    
    return fig

# ==========================================================
# 4. Next-Gen Visual Components
# ==========================================================
def create_radar_strength_chart(metrics):
    """Creates a radar chart showing technical strength across dimensions."""
    categories = ['الاتجاه', 'الزخم', 'RSI', 'السيولة', 'التقلب']
    
    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=[metrics['trend'], metrics['momentum'], metrics['rsi'], metrics['volume'], metrics['volatility']],
        theta=categories,
        fill='toself',
        name='القوة الفنية',
        line_color='#FFD700',
        fillcolor='rgba(255, 215, 0, 0.3)'
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(visible=True, range=[0, 100], color="#888", gridcolor="#333"),
            angularaxis=dict(color="#fff", gridcolor="#333"),
            bgcolor='rgba(0,0,0,0)'
        ),
        showlegend=False,
        paper_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=40, r=40, t=20, b=20),
        height=300
    )
    return fig

def render_sentiment_gauge(score, label, icon, color):
    """HTML/CSS version of a sentiment gauge for premium look."""
    st.markdown(f"""
    <div style='background: rgba(20,20,20,0.8); padding: 20px; border-radius: 15px; border-right: 5px solid {color};'>
        <div style='display: flex; justify-content: space-between; align-items: center;'>
            <h4 style='margin: 0; color: #888;'>الشعور العام</h4>
            <span style='font-size: 1.5rem;'>{icon}</span>
        </div>
        <h2 style='color: {color}; margin: 10px 0;'>{label}</h2>
        <div style='background: #333; height: 10px; border-radius: 5px; margin-top: 10px; overflow: hidden;'>
            <div style='background: {color}; width: {score}%; height: 100%; box-shadow: 0 0 10px {color};'></div>
        </div>
        <p style='margin: 10px 0 0 0; font-size: 0.8rem; color: #666;'>قوة الثيران: {score}%</p>
    </div>
    """, unsafe_allow_html=True)

# ==========================================================
# 5. Strategy Analysis Card
# ==========================================================
def render_strategy_card(df):
    """Renders detailed strategy analysis in Arabic."""
    latest = df.iloc[-1]
    
    # Calculations
    pass_trend = latest['close'] > latest['EMA_200']
    pass_macd = latest['MACD'] > latest['MACD_Signal']
    rsi_val = latest['RSI']
    bb_dist = ((latest['close'] - latest['BBL_20_2.0'])/latest['BBL_20_2.0']*100)
    
    # Overall Score
    score = sum([pass_trend, pass_macd, 30 < rsi_val < 70])
    
    st.markdown("""
    <div style='background: linear-gradient(145deg, rgba(30,30,30,0.95), rgba(10,10,10,0.98)); 
                border: 1px solid rgba(255,215,0,0.3); border-radius: 16px; padding: 25px; margin-top: 20px;'>
    """, unsafe_allow_html=True)
    
    # Score Header
    score_color = "#00ff88" if score >= 2 else "#FFD700" if score == 1 else "#ff4444"
    st.markdown(f"""
    <h3 style='text-align: center; color: {score_color}; margin-bottom: 20px;'>
        {'🟢 إشارة إيجابية' if score >= 2 else '🟡 انتظار' if score == 1 else '🔴 تحذير'}
        <span style='font-size: 0.8em; opacity: 0.7;'>({score}/3)</span>
    </h3>
    """, unsafe_allow_html=True)
    
    # Analysis Details
    col1, col2, col3 = st.columns(3)
    
    with col1:
        icon = "✅" if pass_trend else "❌"
        st.markdown(f"""
        **{icon} تحليل الاتجاه**
        
        السعر: ${latest['close']:,.2f}
        
        المتوسط: ${latest['EMA_200']:,.2f}
        
        الحالة: {'صاعد 📈' if pass_trend else 'هابط 📉'}
        """)
    
    with col2:
        icon = "✅" if pass_macd else "❌"
        st.markdown(f"""
        **{icon} تحليل الزخم**
        
        MACD: {latest['MACD']:.4f}
        
        الإشارة: {latest['MACD_Signal']:.4f}
        
        الحالة: {'صعودي 🚀' if pass_macd else 'هبوطي 🔻'}
        """)
    
    with col3:
        rsi_status = "إفراط شراء ⚠️" if rsi_val > 70 else "إفراط بيع ⚠️" if rsi_val < 30 else "طبيعي ✅"
        st.markdown(f"""
        **📊 مؤشر القوة النسبية**
        
        RSI: {rsi_val:.1f}
        
        البعد عن بولنجر: {bb_dist:.2f}%
        
        الحالة: {rsi_status}
        """)
    
    st.markdown("</div>", unsafe_allow_html=True)

# ==========================================================
# 5. Main Dashboard Layout
# ==========================================================

# --- Premium Header ---
st.markdown("""
<div style='text-align: center; padding: 10px 0;'>
    <h1 style='font-size: 2.5rem; margin: 0; 
               background: linear-gradient(90deg, #FFD700, #fff, #FFD700);
               -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
        🏰 القلعة الذهبية
    </h1>
    <p style='color: #888; margin-top: 5px; font-size: 0.95rem;'>
        منصة تداول مؤسساتية | الإصدار السابع 🪙
    </p>
</div>
""", unsafe_allow_html=True)

st.divider()

# --- Sidebar ---
with st.sidebar:
    st.markdown("""
    <div style='text-align: center; padding: 10px;'>
        <span style='font-size: 3rem;'>🎯</span>
        <h2 style='color: #FFD700; margin: 10px 0;'>لوحة التحكم</h2>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Asset Selector with Icons
    asset_labels = {
        'PAXG/USDT': '🥇 الذهب (PAXG)',
        'BTC/USDT': '₿ بيتكوين (BTC)',
        'ETH/USDT': 'Ξ إيثريوم (ETH)',
        'BNB/USDT': '🔶 بينانس (BNB)',
        'SOL/USDT': '☀️ سولانا (SOL)',
        'XRP/USDT': '💧 ريبل (XRP)',
        'DOGE/USDT': '🐕 دوجكوين (DOGE)'
    }
    selected_symbol = st.selectbox(
        "🎯 اختر الأصل المالي",
        config.TARGET_PAIRS,
        format_func=lambda x: asset_labels.get(x, x)
    )
    
    refresh_rate = st.slider("⏱️ معدل التحديث (ثانية)", 5, 120, 5)
    
    if st.button("🔄 تحديث فوري", use_container_width=True):
        st.cache_data.clear()
        st.rerun()
    
    st.markdown("---")
    
    # Real Portfolio Balance (Phase 9)
    st.markdown("### 💰 المحفظة الحقيقية")
    balance_data = client.get_account_balance()
    if balance_data:
        col_usdt, col_paxg = st.columns(2)
        with col_usdt:
            st.markdown(f"""
            <div style='background: rgba(0,212,255,0.1); border: 1px solid #00d4ff; border-radius: 10px; padding: 10px; text-align: center;'>
                <p style='margin:0; color: #888; font-size: 0.8rem;'>USDT</p>
                <h3 style='margin:0; color: #00d4ff;'>{balance_data['USDT']}</h3>
            </div>
            """, unsafe_allow_html=True)
        with col_paxg:
            st.markdown(f"""
            <div style='background: rgba(255,215,0,0.1); border: 1px solid #FFD700; border-radius: 10px; padding: 10px; text-align: center;'>
                <p style='margin:0; color: #888; font-size: 0.8rem;'>PAXG</p>
                <h3 style='margin:0; color: #FFD700;'>{balance_data['PAXG']}</h3>
            </div>
            """, unsafe_allow_html=True)
        st.markdown(f"<p style='text-align: center; color: #555; font-size: 0.7rem;'>آخر تحديث: {balance_data['timestamp']}</p>", unsafe_allow_html=True)
    else:
        st.warning("⚠️ تعذر جلب الرصيد. تأكد من صلاحيات الـ API")

    st.markdown("---")
    
    # Status Indicators
    st.markdown("""
    <div style='background: rgba(0,255,136,0.1); border: 1px solid #00ff88; 
                border-radius: 10px; padding: 15px; text-align: center;'>
        <span style='font-size: 1.5rem;'>🟢</span>
        <p style='margin: 5px 0; color: #00ff88; font-weight: bold;'>البوت نشط</p>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    is_real = config.SECRET_KEY != 'YOUR_SECRET_KEY_HERE'
    status_color = "#00ff88" if is_real else "#FFD700"
    status_text = "وضع الحساب الحقيقي" if is_real else "وضع المحاكاة"
    status_icon = "🔗" if is_real else "🛡️"
    
    st.markdown(f"""
    <div style='background: rgba({ '0,255,136' if is_real else '255,215,0' },0.1); border: 1px solid {status_color}; 
                border-radius: 10px; padding: 15px; text-align: center;'>
        <span style='font-size: 1.5rem;'>{status_icon}</span>
        <p style='margin: 5px 0; color: {status_color}; font-weight: bold;'>{status_text}</p>
        {f"<p style='margin:0; font-size: 0.7rem; color: #FFA500;'>وضع الاختبار (Testnet) مفعّل</p>" if config.BINANCE_TESTNET_ENABLED else ""}
    </div>
    """, unsafe_allow_html=True)

# --- Main Content Area ---
# Fetch Data
with st.spinner('🔄 جاري تحميل البيانات...'):
    df_chart = client.fetch_data(selected_symbol, config.TIMEFRAME, 300)
    
    if df_chart is not None and not df_chart.empty:
        df_chart = strategy.apply_indicators(df_chart)
        current_price = df_chart.iloc[-1]['close']
        prev_price = df_chart.iloc[-2]['close']
        price_change = current_price - prev_price
        change_pct = (price_change / prev_price) * 100
        high_24h = df_chart['high'].tail(24).max()
        low_24h = df_chart['low'].tail(24).min()
    else:
        current_price = prev_price = price_change = change_pct = high_24h = low_24h = 0

# --- Top Metrics Row ---
st.markdown("<br>", unsafe_allow_html=True)

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
    asset_icon = "🥇" if 'GC' in selected_symbol else "₿" if 'BTC' in selected_symbol else "🪙"
    st.metric(
        label=f"{asset_icon} السعر الحالي",
        value=f"${current_price:,.2f}",
        delta=f"{change_pct:+.2f}%"
    )

with col2:
    trend = df_chart.iloc[-1]['EMA_200'] if df_chart is not None and not df_chart.empty else 0
    trend_icon = "🐂" if current_price > trend else "🐻"
    trend_text = "صاعد" if current_price > trend else "هابط"
    st.metric(
        label=f"{trend_icon} الاتجاه",
        value=trend_text
    )

with col3:
    rsi = df_chart.iloc[-1]['RSI'] if df_chart is not None and not df_chart.empty else 50
    rsi_icon = "🔥" if rsi > 70 else "❄️" if rsi < 30 else "⚖️"
    st.metric(
        label=f"{rsi_icon} RSI",
        value=f"{rsi:.1f}"
    )

with col4:
    st.metric(
        label="📈 أعلى سعر (24س)",
        value=f"${high_24h:,.2f}"
    )

with col5:
    st.metric(
        label="📉 أدنى سعر (24س)",
        value=f"${low_24h:,.2f}"
    )

# --- Tabs ---
tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs([
    "📈 التحليل الفني", 
    "🧠 تحليل الاستراتيجية", 
    "🥇 تحليل الذهب", 
    "🤖 الذكاء الاصطناعي",
    "⚙️ اختبار الاستراتيجية",
    "🎯 التداول الآلي",
    "📜 سجل الإشارات"
])

with tab1:
    if df_chart is not None and not df_chart.empty:
        col_chart, col_radar = st.columns([0.7, 0.3])
        with col_chart:
            st.plotly_chart(
                create_professional_chart(df_chart, selected_symbol),
                use_container_width=True,
                key=f"main_chart"
            )
        with col_radar:
            # Calculate metric scores for Radar
            radar_metrics = {
                'trend': 85 if current_price > trend else 25,
                'momentum': 70 if df_chart.iloc[-1]['MACD'] > df_chart.iloc[-1]['MACD_Signal'] else 30,
                'rsi': float(rsi),
                'volume': 65, # Placeholder for volume strength
                'volatility': 45 # Placeholder
            }
            st.markdown("#### 📊 القوة القفزة")
            st.plotly_chart(create_radar_strength_chart(radar_metrics), use_container_width=True, key=f"radar_chart")
            
            # Sentiment Gauge
            sentiment_score = int(radar_metrics['trend'] * 0.4 + radar_metrics['momentum'] * 0.3 + radar_metrics['rsi'] * 0.3)
            st.markdown("<br>", unsafe_allow_html=True)
            render_sentiment_gauge(
                sentiment_score, 
                "تفاؤل" if sentiment_score > 60 else "تشاؤم" if sentiment_score < 40 else "محايد",
                "🤑" if sentiment_score > 60 else "😰" if sentiment_score < 40 else "😐",
                "#00ff88" if sentiment_score > 60 else "#ff4444" if sentiment_score < 40 else "#FFD700"
            )

with tab2:
    if df_chart is not None and not df_chart.empty:
        render_strategy_card(df_chart)
    else:
        st.warning("⏳ في انتظار البيانات...")

with tab3:
    # --- Gold Dedicated Analysis v2.0 ---
    st.markdown("""
    <div style='text-align: center; padding: 10px; background: linear-gradient(90deg, #FFD700, #FFA500, #FFD700); 
                border-radius: 10px; margin-bottom: 20px;'>
        <h2 style='color: #000; margin: 0;'>🥇 التحليل الذهبي المؤسسي</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Fetch Gold Data
    gold_df = client.fetch_data('PAXG/USDT', config.TIMEFRAME, 300)
    if gold_df is not None and not gold_df.empty:
        gold_df = strategy.apply_indicators(gold_df)
        gold_analysis = gold_analyzer.get_full_analysis(gold_df)
        
        if gold_analysis:
            rec = gold_analysis['recommendation']
            pivots = rec['pivots']
            fib = rec['fibonacci']
            volatility = rec['volatility']
            trend = rec['trend']
            momentum = rec['momentum']
            sentiment = gold_analysis['sentiment']
            
            # === MAIN SIGNAL CARD ===
            signal_color = "#00ff88" if rec['signal'] == "شراء" else "#ff4444" if rec['signal'] == "بيع" else "#FFD700"
            sent_color = sentiment.get('color', '#FFD700')
            
            st.markdown(f"""
            <div style='background: linear-gradient(145deg, rgba(20,20,20,0.98), rgba(5,5,5,0.99)); 
                        border: 3px solid {signal_color}; border-radius: 20px; padding: 30px; margin-bottom: 25px;
                        box-shadow: 0 0 30px {signal_color}40;'>
                <div style='text-align: center;'>
                    <h1 style='color: {signal_color}; font-size: 4rem; margin: 0; text-shadow: 0 0 20px {signal_color};'>
                        {rec['signal_icon']} {rec['signal']}
                    </h1>
                    <div style='margin-top: 15px;'>
                        <span style='background: {signal_color}; color: #000; padding: 8px 25px; border-radius: 20px; font-weight: bold; font-size: 1.3rem;'>
                            نسبة الثقة: {rec['confidence']}%
                        </span>
                    </div>
                    <p style='color: #888; font-size: 1rem; margin-top: 15px;'>
                        المخاطرة/العائد: <strong style='color: #FFD700;'>{rec['risk_reward']}</strong> | 
                        الشعور: <span style='color: {sent_color};'>{sentiment['icon']} {sentiment['sentiment']}</span>
                    </p>
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # === PRICE LEVELS ===
            st.markdown("### 🎯 مستويات التداول")
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("🎯 سعر الدخول", f"${rec['entry']:,.2f}")
            with col2:
                st.metric("🛑 وقف الخسارة", f"${rec['stop_loss']:,.2f}")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("✅ الهدف الأول", f"${rec['take_profit_1']:,.2f}")
            with col2:
                st.metric("✅ الهدف الثاني", f"${rec['take_profit_2']:,.2f}")
            with col3:
                st.metric("✅ الهدف الثالث", f"${rec['take_profit_3']:,.2f}")
            
            st.divider()
            
            # --- Analysis Reasons ---
            st.markdown("### 📊 أسباب التوصية:")
            for i, reason in enumerate(rec['reasons'], 1):
                st.markdown(f"**{i}.** {reason}")
            
            st.divider()
            
            # --- Pivot Points & Fibonacci ---
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### 📍 نقاط البيفوت")
                if pivots:
                    st.markdown(f"""
                    | المستوى | السعر |
                    |---------|-------|
                    | **R3** | ${pivots.get('r3', 0):,.2f} |
                    | **R2** | ${pivots.get('r2', 0):,.2f} |
                    | **R1** | ${pivots.get('r1', 0):,.2f} |
                    | **Pivot** | ${pivots.get('pivot', 0):,.2f} |
                    | **S1** | ${pivots.get('s1', 0):,.2f} |
                    | **S2** | ${pivots.get('s2', 0):,.2f} |
                    | **S3** | ${pivots.get('s3', 0):,.2f} |
                    """)
            
            with col2:
                st.markdown("### 📐 مستويات فيبوناتشي")
                if fib:
                    st.markdown(f"""
                    | المستوى | السعر |
                    |---------|-------|
                    | **High** | ${fib.get('high', 0):,.2f} |
                    | **23.6%** | ${fib.get('fib_236', 0):,.2f} |
                    | **38.2%** | ${fib.get('fib_382', 0):,.2f} |
                    | **50.0%** | ${fib.get('fib_500', 0):,.2f} |
                    | **61.8%** | ${fib.get('fib_618', 0):,.2f} |
                    | **78.6%** | ${fib.get('fib_786', 0):,.2f} |
                    | **Low** | ${fib.get('low', 0):,.2f} |
                    """)
            
            st.divider()
            
            # --- Trend & Indicators ---
            st.markdown("### 📊 المؤشرات الفنية")
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                trend_icon = trend.get('icon', '⚪')
                trend_dir = trend.get('direction', 'غير محدد')
                st.metric("الاتجاه", f"{trend_icon} {trend_dir}")
            
            with col2:
                rsi_val = momentum.get('rsi', 50)
                st.metric("RSI", f"{rsi_val}")
            
            with col3:
                macd_status = momentum.get('macd_status', '')
                st.metric("MACD", macd_status)
            
            with col4:
                mom_status = momentum.get('momentum_status', '')
                st.metric("الزخم", mom_status)
            
            # Volatility info
            if volatility:
                risk_color = "#ff4444" if volatility['risk_level'] in ["عالي", "عالي جداً"] else "#FFD700" if volatility['risk_level'] == "متوسط" else "#00ff88"
                st.info(f"⚡ **التقلب:** {volatility['status']} | ATR: ${volatility['atr']:,.2f} ({volatility['atr_pct']:.2f}%) | المخاطرة: {volatility['risk_level']}")
            
            # Score breakdown
            st.markdown(f"""
            <div style='background: rgba(30,30,30,0.9); border-radius: 10px; padding: 15px; margin-top: 10px;'>
                <span style='color: #00ff88; font-weight: bold;'>🟢 نقاط الشراء: {rec['buy_score']}</span>
                &nbsp;&nbsp;|&nbsp;&nbsp;
                <span style='color: #ff4444; font-weight: bold;'>🔴 نقاط البيع: {rec['sell_score']}</span>
            </div>
            """, unsafe_allow_html=True)
        
        else:
            st.warning("⏳ في انتظار بيانات كافية للتحليل...")
    else:
        st.error("❌ فشل في جلب بيانات الذهب")

with tab4:
    # === AI Analysis Tab ===
    st.markdown("### 🤖 التحليل بالذكاء الاصطناعي")
    
    if df_chart is not None and not df_chart.empty:
        # Get AI analysis
        ai_score = ai_analyzer.get_ai_score(df_chart)
        pattern = ai_analyzer.detect_chart_patterns(df_chart)
        
        # Display AI Score Gauge
        col_ai1, col_ai2, col_ai3 = st.columns(3)
        
        with col_ai1:
            score_color = "#00ff88" if ai_score['score'] > 60 else ("#FFD700" if ai_score['score'] > 40 else "#ff4444")
            st.markdown(f"""
            <div style='background: rgba(30,30,30,0.9); border: 2px solid {score_color}; border-radius: 15px; padding: 20px; text-align: center;'>
                <p style='color: #888; font-size: 0.9rem; margin: 0;'>نقاط الذكاء الاصطناعي</p>
                <h1 style='color: {score_color}; margin: 10px 0; font-size: 3rem;'>{ai_score['score']}</h1>
                <p style='color: #888; font-size: 0.8rem; margin: 0;'>من 100</p>
            </div>
            """, unsafe_allow_html=True)
        
        with col_ai2:
            st.metric("🔍 النمط المكتشف", pattern['pattern'])
            st.metric("📊 الاتجاه المتوقع", ai_score['trend'])
        
        with col_ai3:
            st.metric("📰 المعنويات", ai_score['sentiment'])
            signal_text = "شراء قوي" if ai_score['score'] > 70 else ("بيع قوي" if ai_score['score'] < 30 else "محايد")
            st.metric("🎯 التوصية", signal_text)
        
        # Pattern Details
        if pattern['confidence'] > 0:
            st.markdown("---")
            st.markdown(f"""
            <div style='background: rgba(255,215,0,0.1); border-left: 4px solid #FFD700; padding: 15px; border-radius: 5px;'>
                <h4 style='color: #FFD700; margin: 0 0 10px 0;'>🔍 تفاصيل النمط</h4>
                <p style='margin: 5px 0;'><strong>النمط:</strong> {pattern['pattern']}</p>
                <p style='margin: 5px 0;'><strong>الإشارة:</strong> {pattern['signal']}</p>
                <p style='margin: 5px 0;'><strong>الثقة:</strong> {pattern['confidence']}%</p>
            </div>
            """, unsafe_allow_html=True)
    else:
        st.warning("⚠️ لا توجد بيانات كافية للتحليل")

with tab5:
    # === Backtesting Tab ===
    st.markdown("### ⚙️ اختبار الاستراتيجية")
    
    col_bt1, col_bt2 = st.columns([1, 3])
    
    with col_bt1:
        st.markdown("#### الإعدادات")
        bt_days = st.slider("فترة الاختبار (أيام)", 30, 365, 180, key="backtesting_days")
        bt_capital = st.number_input("رأس المال ($)", value=10000, step=1000, key="backtesting_capital")
        
        if st.button("🚀 تشغيل الاختبار", use_container_width=True):
            with st.spinner("جاري اختبار الاستراتيجية..."):
                # Load historical data
                bt_df = client.fetch_data(selected_symbol, '1h', bt_days * 24)
                
                if bt_df is not None and not bt_df.empty:
                    # Run backtest
                    backtester.initial_capital = bt_capital
                    trades, equity = backtester.run_backtest(selected_symbol, bt_df)
                    metrics = backtester.calculate_metrics(trades, equity)
                    
                    # Store in session state
                    st.session_state['bt_metrics'] = metrics
                    st.session_state['bt_equity'] = equity
                    st.rerun()
    
    with col_bt2:
        if 'bt_metrics' in st.session_state:
            metrics = st.session_state['bt_metrics']
            
            # Display Metrics
            st.markdown("#### 📊 نتائج الاختبار")
            
            col_m1, col_m2, col_m3, col_m4 = st.columns(4)
            col_m1.metric("إجمالي الصفقات", metrics['total_trades'])
            col_m2.metric("نسبة النجاح", f"{metrics['win_rate']}%")
            col_m3.metric("معامل الربح", metrics['profit_factor'])
            col_m4.metric("أقصى انخفاض", f"{metrics['max_drawdown']}%")
            
            col_m5, col_m6, col_m7, col_m8 = st.columns(4)
            col_m5.metric("الربح/الخسارة", f"${metrics['total_pnl']}")
            col_m6.metric("متوسط الربح", f"${metrics['avg_win']}")
            col_m7.metric("متوسط الخسارة", f"${metrics['avg_loss']}")
            col_m8.metric("العائد", f"{metrics['return_pct']}%")
            
            # Equity Curve
            if 'bt_equity' in st.session_state:
                equity = st.session_state['bt_equity']
                
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    y=equity,
                    mode='lines',
                    name='رأس المال',
                    line=dict(color='#FFD700', width=2),
                    fill='tozeroy',
                    fillcolor='rgba(255,215,0,0.1)'
                ))
                
                fig.update_layout(
                    title="منحنى رأس المال",
                    template='plotly_dark',
                    height=400,
                    xaxis_title="الصفقات",
                    yaxis_title="رأس المال ($)",
                    showlegend=False
                )
                
                st.plotly_chart(fig, use_container_width=True, key=f"equity_curve")
        else:
            st.info("👈 اضبط الإعدادات وانقر على 'تشغيل الاختبار'")

    # === Live Trading Tab (Phase 10) ===
    st.markdown("### 🎯 محرك التداول الآلي (بث مباشر)")
    
    # --- Approval Queue (NEW) ---
    st.markdown("#### ⏳ صفقات في انتظار الموافقة")
    pending_signals = database.get_pending_signals()
    
    if not pending_signals.empty:
        for index, row in pending_signals.iterrows():
            with st.container():
                # Use a specific style for signal cards
                color = "#00ff88" if row['type'] == 'BUY' else "#ff4444"
                st.markdown(f"""
                <div style='border: 1px solid {color}; border-radius: 10px; padding: 15px; margin-bottom: 10px; background: rgba(0,0,0,0.2);'>
                    <div style='display: flex; justify-content: space-between;'>
                        <strong style='color: {color};'>{row['type']} - {row['symbol']}</strong>
                        <span style='color: #888; font-size: 0.8rem;'>{row['timestamp']}</span>
                    </div>
                    <p style='margin: 5px 0;'>سعر الدخول: ${row['price']:.2f} | وقف الخسارة: ${row['stop_loss']:.2f} | الهدف: ${row['take_profit']:.2f}</p>
                    <p style='font-size: 0.8rem; color: #aaa;'>السبب: {row['reason']}</p>
                </div>
                """, unsafe_allow_html=True)
                
                col_acc, col_rej, _ = st.columns([1, 1, 4])
                if col_acc.button("✅ قبول الصفقة", key=f"acc_{row['id']}", use_container_width=True):
                    database.update_signal_status(row['id'], 'APPROVED')
                    st.success(f"تمت الموافقة على صفقة {row['symbol']}! جاري التنفيذ...")
                    time.sleep(1)
                    st.rerun()
                if col_rej.button("❌ رفض", key=f"rej_{row['id']}", use_container_width=True):
                    database.update_signal_status(row['id'], 'REJECTED')
                    st.warning(f"تم رفض إشارة {row['symbol']}.")
                    time.sleep(1)
                    st.rerun()
    else:
        st.write("✅ لا توجد إشارات معلقة حالياً.")

    st.divider()

    # --- Quick Manual Trade (NEW) ---
    st.markdown("#### ⚡ تنفيذ صفقة سريعة (يدوي)")
    col_qt1, col_qt2, col_qt3 = st.columns([2, 1, 1])
    
    with col_qt1:
        qt_symbol = st.selectbox("اختر العملة", config.TARGET_PAIRS, key="qt_symbol")
    with col_qt2:
        qt_type = st.radio("النوع", ["BUY", "SELL"], horizontal=True, key="qt_type")
    with col_qt3:
        qt_execute = st.button("🚀 تنفيذ فوراً", use_container_width=True)
        
    if qt_execute:
        with st.spinner("جاري التنفيذ..."):
            # Price and Risk
            curr_p = client.get_current_price(qt_symbol)
            atr = 0.01 * curr_p # Simple 1% mock ATR for manual trade
            sl = curr_p - (atr * 1.5) if qt_type == "BUY" else curr_p + (atr * 1.5)
            tp = curr_p + (atr * 2.0) if qt_type == "BUY" else curr_p - (atr * 2.0)
            
            # Log as APPROVED so the bot picks it up
            database.log_signal(qt_symbol, qt_type, curr_p, sl, tp, "تنفيذ يدوي سريع من لوحة التحكم", "APPROVED")
            st.success(f"تم إرسال أمر {qt_type} لـ {qt_symbol} للمحرك!")
            time.sleep(1)
            st.rerun()

    st.divider()
    
    # Get Stats
    stats = database.calculate_stats()
    
    col_s1, col_s2, col_s3, col_s4 = st.columns(4)
    col_s1.metric("إجمالي الربح/الخسارة", f"${stats['total_pnl']}", delta=f"{stats['total_pnl']}$")
    col_s2.metric("نسبة النجاح", f"{stats['win_rate']}%")
    col_s3.metric("عدد الصفقات المنفذة", stats['total_trades'])
    col_s4.metric("أفضل صفقة", f"${stats['best_trade']}")

    st.divider()
    
    # Active Positions
    st.markdown("#### 🟢 الصفقات المفتوحة حالياً")
    active_pos = database.get_active_positions()
    if active_pos:
        pos_list = []
        for sym, data in active_pos.items():
            current_p = client.get_current_price(sym)
            pnl = (current_p - data['entry']) * data['size'] if data['type'] == 'LONG' else (data['entry'] - current_p) * data['size']
            pnl_pct = (pnl / (data['entry'] * data['size'])) * 100
            
            pos_list.append({
                'الرمز': sym,
                'النوع': data['type'],
                'سعر الدخول': f"${data['entry']:.2f}",
                'السعر الحالي': f"${current_p:.2f}",
                'الكمية': f"{data['size']:.4f}",
                'الربح/الخسارة': f"${pnl:.2f}",
                'النسبة': f"{pnl_pct:+.2f}%",
                'وقت الفتح': data['opened_at']
            })
        st.table(pd.DataFrame(pos_list))
    else:
        st.info("ℹ️ لا توجد صفقات مفتوحة حالياً. المحرك يراقب السوق...")

    st.divider()

    # Trade History
    st.markdown("#### 📜 تاريخ الصفقات المكتملة")
    history_df = database.get_trade_history(50)
    if not history_df.empty:
        # Translate and format
        disp_history = history_df[['symbol', 'type', 'entry_price', 'exit_price', 'profit_loss', 'exit_reason', 'exit_time']].copy()
        disp_history.columns = ['🪙 الرمز', '📊 النوع', '🎯 دخول', '🏁 خروج', '💰 الربح', '📝 السبب', '⏰ الوقت']
        st.dataframe(disp_history, use_container_width=True)
    else:
        st.info("🔍 لا يوجد تاريخ صفقات حتى الآن.")

with tab7:
    signals_df = database.get_recent_signals(50)
    if not signals_df.empty:
        display_signals = signals_df[['timestamp', 'symbol', 'type', 'price', 'stop_loss', 'take_profit', 'status', 'reason']].copy()
        display_signals.columns = ['⏰ التوقيت', '🪙 الأصل', '📊 النوع', '🎯 الدخول', '🛑 وقف الخسارة', '✅ الهدف', '📌 الحالة', '📝 السبب']
        st.dataframe(display_signals, use_container_width=True)
    else:
        st.info("🔍 لا توجد توصيات مسجلة حتى الآن. الصبر مفتاح الربح!")

# Footer Timestamp
st.markdown(f"""
<div style='text-align: center; color: #666; margin-top: 20px; font-size: 0.85rem;'>
    آخر تحديث: {time.strftime('%Y-%m-%d %H:%M:%S')} 🕐
</div>
""", unsafe_allow_html=True)
