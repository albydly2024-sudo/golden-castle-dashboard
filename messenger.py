import aiohttp
import asyncio
from loguru import logger
from config import config

class TelegramMessenger:
    def __init__(self):
        self.token = config.TELEGRAM_TOKEN
        self.chat_id = config.TELEGRAM_CHAT_ID
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.session = None

    async def ensure_session(self):
        """Ensure aiohttp session is created within the running loop."""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()

    async def send_message(self, text, reply_markup=None, chat_id=None):
        """Send a message asynchronously to the configured Telegram chat or a specific ID."""
        target_chat = chat_id or self.chat_id
        if not self.token or not target_chat:
            logger.warning("Telegram not configured or no target chat. Skipping alert.")
            return

        try:
            await self.ensure_session()
            payload = {
                "chat_id": target_chat,
                "text": text,
                "parse_mode": "Markdown"
            }
            if reply_markup:
                payload["reply_markup"] = reply_markup
                
            async with self.session.post(f"{self.base_url}/sendMessage", json=payload) as resp:
                return resp.status == 200
        except Exception as e:
            logger.error(f"Error sending Telegram alert: {e}")
            return False

    async def get_updates(self):
        """Fetch new messages from Telegram asynchronously."""
        if not self.token: return []
        try:
            await self.ensure_session()
            url = f"{self.base_url}/getUpdates?offset={self.offset}&timeout=1"
            async with self.session.get(url) as resp:
                if resp.status == 200:
                    data = await resp.json()
                    updates = data.get("result", [])
                    if updates:
                        logger.info(f"📥 Raw Telegram Updates: {len(updates)} received.")
                        self.offset = updates[-1]["update_id"] + 1
                    return updates
        except Exception as e:
            logger.error(f"Error fetching Telegram updates: {e}")
        return []

    async def close(self):
        """Close the aiohttp session."""
        if self.session and not self.session.closed:
            await self.session.close()

messenger = TelegramMessenger()
