@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🚀 Golden Castle - Auto GitHub Uploader
echo ===================================================

:: Check for gh command
where gh >nul 2>nul
if %errorlevel% neq 0 (
    echo ⚠️ 'gh' command not found in PATH.
    echo Please restart this terminal or your computer to update PATH.
    echo OR, I will try to find it manually...
    if exist "C:\Program Files\GitHub CLI\gh.exe" (
        set GH_CMD="C:\Program Files\GitHub CLI\gh.exe"
    ) else (
        echo ❌ Could not find gh.exe. Please restart and try again.
        pause
        exit /b
    )
) else (
    set GH_CMD=gh
)

echo 🔑 Authentication Step
echo You need to login to GitHub. 
echo 1. Select 'GitHub.com' -> 'HTTPS' -> 'Y' (Yes to authenticate) -> 'Login with a web browser'
echo 2. Copy the one-time code shown.
echo 3. Paste it in the browser window that opens.
echo.
%GH_CMD% auth login

echo.
echo 📦 Creating Repository 'golden-castle-dashboard'...
%GH_CMD% repo create golden-castle-dashboard --private --source=. --remote=origin --push

echo.
echo ===================================================
echo ✅ Upload Complete!
echo ===================================================
echo Your code is now safe on GitHub.
pause
