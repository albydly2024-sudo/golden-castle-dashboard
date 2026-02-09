@echo off
echo STARTING TRADING BOT...
echo.
echo Checking for Python...
set "PY_CMD="

python --version >nul 2>&1
if %errorlevel% equ 0 (set "PY_CMD=python") else (
    python3 --version >nul 2>&1
    if %errorlevel% equ 0 (set "PY_CMD=python3") else (
        py --version >nul 2>&1
        if %errorlevel% equ 0 (set "PY_CMD=py")
    )
)

if "%PY_CMD%"=="" (
    echo [ERROR] Python not found!
    echo.
    echo Please download and install Python from: https://www.python.org/downloads/
    echo ** IMPORTANT: During installation, YOU MUST check the box: **
    echo    "Add Python to PATH"
    echo.
    pause
    exit /b
)

echo Found Python: %PY_CMD%
echo.

echo Installing/Updating dependencies...
%PY_CMD% -m pip install -r requirements.txt

echo.
echo Checking for .env file...
if not exist .env (
    echo [WARNING] .env file not found. Creating a temporary one for Paper Trading...
    echo EXCHANGE_NAME=binance > .env
    echo TRADING_MODE=paper >> .env
    echo TRADING_SYMBOL=BTC/USDT >> .env
)

echo.
echo Launching Bot...
%PY_CMD% bot.py
pause
