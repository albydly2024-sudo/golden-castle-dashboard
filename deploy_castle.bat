@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🏰 Golden Castle - Deployment Protocol
echo ===================================================

:: 1. Check for cloudflared.exe
if not exist "cloudflared.exe" (
    echo ☁️ Cloudflared not found. Downloading...
    powershell -Command "Invoke-WebRequest -Uri 'https://github.com/cloudflare/cloudflared/releases/latest/download/cloudflared-windows-amd64.exe' -OutFile 'cloudflared.exe'"
    if not exist "cloudflared.exe" (
        echo ❌ Failed to download cloudflared. Please download it manually.
        pause
        exit /b
    )
    echo ✅ Cloudflared installed.
)

:: 2. Kill previous instances
taskkill /F /IM streamlit.exe >nul 2>&1
taskkill /F /IM cloudflared.exe >nul 2>&1

:: 3. Start Streamlit Dashboard in Background
echo 🚀 Starting Dashboard...
start /B streamlit run dashboard.py --server.port 8501 --theme.base dark > streamlit_log.txt 2>&1

:: Wait for Streamlit to warm up
timeout /t 10 /nobreak >nul

:: 4. Start Tunnel Loop
:TUNNEL_LOOP
echo 🌐 Establishing Secure Tunnel...
cloudflared tunnel --url http://localhost:8501 > tunnel_log.txt 2>&1
echo ⚠️ Tunnel disconnected! Restarting in 5 seconds...
timeout /t 5
goto TUNNEL_LOOP
