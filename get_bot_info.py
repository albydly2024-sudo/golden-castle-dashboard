import asyncio
import aiohttp

async def get_bot_info():
    token = '8524067770:AAF9OfxWWZNkt494CPTDss5l7SZVzmhOzDU'
    url = f'https://api.telegram.org/bot{token}/getMe'
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            print(await response.json())

if __name__ == "__main__":
    asyncio.run(get_bot_info())
