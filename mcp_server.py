import os
import asyncio
import ccxt.async_support as ccxt
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load environment variables
load_dotenv()

# Configuration
EXCHANGE_NAME = os.getenv('EXCHANGE_NAME', 'binance')
API_KEY = os.getenv('API_KEY')
SECRET_KEY = os.getenv('SECRET_KEY')

# Initialize FastMCP Server
mcp = FastMCP("CryptoTradingBot")

async def get_exchange():
    """Initialize exchange connection."""
    exchange_class = getattr(ccxt, EXCHANGE_NAME)
    return exchange_class({
        'apiKey': API_KEY,
        'secret': SECRET_KEY,
        'enableRateLimit': True,
    })

@mcp.tool()
async def get_account_balance() -> str:
    """Get the current account balance for all non-zero assets."""
    exchange = await get_exchange()
    try:
        balance = await exchange.fetch_balance()
        total_balance = balance['total']
        
        # Filter for non-zero balances
        active_balances = {k: v for k, v in total_balance.items() if v > 0}
        
        if not active_balances:
            return "No active balances found."
            
        report = "💰 **Account Balance**:\n"
        for asset, amount in active_balances.items():
            report += f"- **{asset}**: {amount}\n"
            
        return report
    except Exception as e:
        return f"Error fetching balance: {str(e)}"
    finally:
        await exchange.close()

@mcp.tool()
async def get_crypto_price(symbol: str) -> str:
    """Get the current price of a cryptocurrency (e.g., BTC/USDT)."""
    exchange = await get_exchange()
    try:
        symbol = symbol.upper()
        if '/' not in symbol: 
            symbol += '/USDT' # Default to USDT pair if not specified
            
        ticker = await exchange.fetch_ticker(symbol)
        price = ticker['last']
        return f"💵 **{symbol}**: {price}"
    except Exception as e:
        return f"Error fetching price for {symbol}: {str(e)}"
    finally:
        await exchange.close()

@mcp.tool()
async def get_market_sentiment() -> str:
    """Get the current Fear & Greed Index for the crypto market."""
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get('https://api.alternative.me/fng/') as resp:
                data = await resp.json()
                value = int(data['data'][0]['value'])
                classification = data['data'][0]['value_classification']
                return f"🧠 **Market Sentiment**: {classification} ({value})"
    except Exception as e:
        return f"Error fetching sentiment: {str(e)}"

if __name__ == "__main__":
    # Run the MCP server
    mcp.run()

@mcp.tool()
async def execute_trade(symbol: str, side: str, amount: float, type: str = 'market', price: float = None) -> str:
    """
    Execute a crypto trade.
    
    Args:
        symbol: e.g. "BTC/USDT"
        side: "buy" or "sell"
        amount: Quantity to trade
        type: "market" or "limit"
        price: Price for limit orders (required if type is limit)
    """
    exchange = await get_exchange()
    try:
        symbol = symbol.upper()
        if '/' not in symbol: symbol += '/USDT'
        
        # Basic validation
        if side.lower() not in ['buy', 'sell']:
            return "Error: Side must be 'buy' or 'sell'"
            
        if type.lower() == 'limit' and not price:
            return "Error: Price is required for limit orders"
            
        order = await exchange.create_order(symbol, type, side, amount, price)
        return f"✅ **Order Executed**:\nID: {order['id']}\nStatus: {order['status']}\nDetails: {side} {amount} {symbol}"
    except Exception as e:
        return f"❌ Trade Failed: {str(e)}"
    finally:
        await exchange.close()

@mcp.tool()
async def list_open_orders(symbol: str = None) -> str:
    """List all active/open orders."""
    exchange = await get_exchange()
    try:
        if symbol:
            symbol = symbol.upper()
            if '/' not in symbol: symbol += '/USDT'
            orders = await exchange.fetch_open_orders(symbol)
        else:
            orders = await exchange.fetch_open_orders()
            
        if not orders:
            return "No open orders found."
            
        report = "📋 **Open Orders**:\n"
        for o in orders:
            report += f"- [{o['id']}] {o['side'].upper()} {o['amount']} {o['symbol']} @ {o['price']}\n"
        return report
    except Exception as e:
        return f"Error fetching orders: {str(e)}"
    finally:
        await exchange.close()

@mcp.tool()
async def cancel_order(order_id: str, symbol: str) -> str:
    """Cancel a specific order by ID."""
    exchange = await get_exchange()
    try:
        symbol = symbol.upper()
        if '/' not in symbol: symbol += '/USDT'
        
        await exchange.cancel_order(order_id, symbol)
        return f"✅ Order {order_id} cancelled successfully."
    except Exception as e:
        return f"❌ Failed to cancel order: {str(e)}"
    finally:
        await exchange.close()
