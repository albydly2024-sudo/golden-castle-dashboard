@echo off
setlocal
cd /d "%~dp0"

echo ===================================================
echo 🚀 Golden Castle - Ultimate Publisher
echo ===================================================

:: Force config to be local
mkdir .gh_config 2>nul
set GH_CONFIG_DIR=%~dp0.gh_config

:: Find GH
if exist "C:\Program Files\GitHub CLI\gh.exe" (
    set GH_CMD="C:\Program Files\GitHub CLI\gh.exe"
) else (
    set GH_CMD=gh
)

:: Auth
echo.
echo 🔑 Please authorize in the browser...
%GH_CMD% auth login --web --git-protocol https

:: Create & Push
echo.
echo 📦 Creating Repository...
%GH_CMD% repo create golden-castle-dashboard --private --source=. --remote=origin --push

if %errorlevel% neq 0 (
    echo.
    echo ⚠️ Repo might exist. Pushing updates...
    git push -u origin main
)

echo.
echo ===================================================
echo ✅ DONE! Your code is on GitHub.
echo ===================================================
pause
