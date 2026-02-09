# Golden Citadel - Crypto Trading Bot & Dashboard

Professional trading terminal with Binance and Gold (Yahoo Finance) support.

## Project Structure
- `bot_main.py`: Main bot engine for scanning and logging signals.
- `dashboard.py`: Streamlit-based web interface for monitoring.
- `market_data.py`: Data fetching layer (Binance via CCXT, Gold via yfinance).
- `strategy.py`: Technical analysis and signal generation.

## Deployment Instructions

### 1. Dashboard (Streamlit Cloud)
1. Push this folder to a GitHub repository.
2. Go to [share.streamlit.io](https://share.streamlit.io).
3. Connect your GitHub and select the repository.
4. Set the main file to `dashboard.py`.
5. In "Secrets", add the environment variables from `.env.example`.

### 2. Bot Engine (Render / Railway)
1. Use the same GitHub repository.
2. Create a new "Background Worker" (Render) or Service (Railway).
3. Set the build command to `pip install -r requirements.txt`.
4. Set the start command to `python bot_main.py`.
5. Add environment variables.

## Environment Variables
See `.env.example` for the required keys.
