@echo off
echo ========================================
echo Turkish Airlines Flight Price Monitor
echo Setup Script
echo ========================================
echo.

echo [1/3] Installing Python dependencies...
pip install -r requirements.txt

echo.
echo [2/3] Checking Chrome installation...
where chrome >nul 2>&1
if %errorlevel% equ 0 (
    echo ✓ Chrome is installed
) else (
    echo ⚠ Chrome not found. Please install Google Chrome.
    echo Download from: https://www.google.com/chrome/
)

echo.
echo [3/3] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. Edit config.json with your settings
echo 2. Set up notifications (see README.md)
echo 3. Run: python flight_monitor.py
echo.
echo For Telegram setup (recommended):
echo - Message @BotFather on Telegram
echo - Create a new bot
echo - Get your chat ID from @userinfobot
echo.
pause
