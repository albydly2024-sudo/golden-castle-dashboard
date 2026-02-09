import requests
import config
import os

def send_telegram_message(message):
    """
    Sends a message to the Telegram chat.
    """
    # Check if Telegram is configured
    if not hasattr(config, 'TELEGRAM_TOKEN') or not hasattr(config, 'TELEGRAM_CHAT_ID'):
        print("⚠️ Telegram not configured. Skipping alert.")
        return

    token = config.TELEGRAM_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    if token == "YOUR_TOKEN" or chat_id == "YOUR_CHAT_ID":
         print("⚠️ Telegram placeholders found. Skipping alert.")
         return

    url = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {
        "chat_id": chat_id,
        "text": message,
        "parse_mode": "Markdown"
    }
    
    try:
        response = requests.post(url, json=payload)
        if response.status_code != 200:
            print(f"Failed to send Telegram message: {response.text}")
    except Exception as e:
        print(f"Error sending Telegram message: {e}")

def send_telegram_photo(photo_path, caption=""):
    """
    Sends a photo to Telegram with optional caption.
    """
    if not hasattr(config, 'TELEGRAM_TOKEN') or not hasattr(config, 'TELEGRAM_CHAT_ID'):
        print("⚠️ Telegram not configured. Skipping photo.")
        return
    
    token = config.TELEGRAM_TOKEN
    chat_id = config.TELEGRAM_CHAT_ID
    
    if token == "YOUR_TOKEN" or chat_id == "YOUR_CHAT_ID":
         print("⚠️ Telegram placeholders found. Skipping photo.")
         return
    
    if not os.path.exists(photo_path):
        print(f"❌ Photo not found: {photo_path}")
        return
    
    url = f"https://api.telegram.org/bot{token}/sendPhoto"
    
    try:
        with open(photo_path, 'rb') as photo:
            files = {'photo': photo}
            data = {
                'chat_id': chat_id,
                'caption': caption,
                'parse_mode': 'Markdown'
            }
            response = requests.post(url, files=files, data=data)
            
            if response.status_code != 200:
                print(f"Failed to send photo: {response.text}")
            else:
                print(f"✅ Photo sent successfully")
    except Exception as e:
        print(f"Error sending photo: {e}")

def send_signal_alert(symbol, setup, chart_path=None):
    """
    Formats a professional signal alert in Arabic and sends with chart.
    """
    signal_emoji = "🚀" if setup['type'] == "LONG" else "📉"
    signal_ar = "شراء" if setup['type'] == "LONG" else "بيع"
    
    msg = f"""
{signal_emoji} **فرصة تداول جديدة!**
**العملة:** {symbol}
**النوع:** {signal_ar}

💰 **سعر الدخول:** ${setup['entry']:.2f}
🛑 **وقف الخسارة:** ${setup['stop_loss']:.2f}
🎯 **الهدف:** ${setup['take_profit']:.2f}

📝 **السبب:** {setup['reason']}
    """
    
    # Send chart first if available
    if chart_path and os.path.exists(chart_path):
        send_telegram_photo(chart_path, f"📊 {symbol} - إشارة {signal_ar}")
    
    # Then send message
    send_telegram_message(msg)

def send_position_update(symbol, update_type, price, profit_pct=None):
    """
    Send position update (TP hit, SL hit, etc.)
    """
    if update_type == "TP":
        emoji = "🎯✅"
        title = "تم تحقيق الهدف!"
        color = "الربح"
    elif update_type == "SL":
        emoji = "🛑"
        title = "تم إيقاف الخسارة"
        color = "الخسارة"
    else:
        emoji = "ℹ️"
        title = "تحديث الصفقة"
        color = ""
    
    profit_text = f"\n💰 **النسبة:** {profit_pct:+.2f}%" if profit_pct else ""
    
    msg = f"""
{emoji} **{title}**
**العملة:** {symbol}
💵 **السعر:** ${price:.2f}{profit_text}
    """
    send_telegram_message(msg)

def send_risk_alert(message):
    """
    Send risk warning alert.
    """
    msg = f"""
⚠️ **تحذير إدارة المخاطر**

{message}
    """
    send_telegram_message(msg)
