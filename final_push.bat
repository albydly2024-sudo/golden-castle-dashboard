@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🚀 Golden Castle - Final Push
echo ===================================================

echo.
echo 📡 Connecting to GitHub...
git remote set-url origin https://github.com/albydly2024-sudo/golden-castle-dashboard.git

echo.
echo ⬆️ Uploading files...
echo (If a window pops up, please sign in!)
echo.

git push -u origin main

echo.
if %errorlevel% equ 0 (
    echo ✅ SUCCESS! Your code is now online.
) else (
    echo ❌ Upload failed. Please check your internet or sign-in.
)
pause
