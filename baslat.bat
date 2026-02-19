@echo off
REM ===================================================================
REM Cryptocurrency Trading Bot - Baslat Script
REM ===================================================================

echo.
echo ====================================================================
echo          CRYPTOCURRENCY TRADING BOT
echo ====================================================================
echo.
echo MOD: Kagit Trading (Simulasyon - Gercek para riski YOK)
echo.
echo Bot baslatiiliyor...
echo Durdurmak icin: Ctrl+C
echo.
echo Log dosyasi: logs\trading_bot.log
echo Veritabani: data\trading_bot.db
echo.
python src/main.py
pause
