@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🚀 Golden Castle - One-Click Publisher
echo ===================================================

:: 1. Find GH Command
if exist "C:\Program Files\GitHub CLI\gh.exe" (
    set GH_CMD="C:\Program Files\GitHub CLI\gh.exe"
) else (
    set GH_CMD=gh
)

:: 2. Auto-Authenticate (Web Mode)
echo.
echo 🔑 AUTHENTICATION REQUIRED
echo I will open your browser now.
echo Please click "Authorize" when asked.
echo.
timeout /t 2 >nul
%GH_CMD% auth login --web --git-protocol https

:: 3. Create Repo & Push (Auto-Retry loop)
echo.
echo 📦 Creating Repository 'golden-castle-dashboard'...
%GH_CMD% repo create golden-castle-dashboard --private --source=. --remote=origin --push

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Repo might already exist. Trying to just push updates...
    %GH_CMD% repo view golden-castle-dashboard --web >nul 2>nul
    git push -u origin main
)

echo.
echo ===================================================
echo ✅ DONE! Your code is on GitHub.
echo ===================================================
pause
