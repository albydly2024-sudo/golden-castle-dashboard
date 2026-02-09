@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🚀 Golden Castle - GitHub Uploader
echo ===================================================

:: 1. Configure Git (If not already done)
echo 🔧 Configuring Git...
set /p EMAIL="Enter your GitHub Email: "
set /p NAME="Enter your GitHub Name: "
git config --global user.email "%EMAIL%"
git config --global user.name "%NAME%"

:: 2. Create Repository Instructions
echo.
echo ===================================================
echo ⚠️ ACTION REQUIRED: Create a New Repository
echo ===================================================
echo 1. Go to: https://github.com/new
echo 2. Repository name: golden-castle-dashboard
echo 3. Visibility: Private (Recommended)
echo 4. Click "Create repository"
echo 5. Copy the HTTPS URL (e.g., https://github.com/StartYourOwn/golden-castle.git)
echo.

set /p REPO_URL="Paste the Repository URL here: "

:: 3. Push Code
echo.
echo 📦 Packaging code...
git add .
git commit -m "Initial release of Golden Castle v2.0"

echo.
echo 🚀 Pushing to GitHub...
git branch -M main
git remote add origin %REPO_URL%
git push -u origin main

echo.
echo ===================================================
echo ✅ Upload Complete!
echo ===================================================
echo Now go to https://share.streamlit.io/ to deploy your app.
pause
