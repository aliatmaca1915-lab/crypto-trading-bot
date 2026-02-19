@echo off
REM ===================================================================
REM Cryptocurrency Trading Bot - Windows Kurulum Scripti
REM ===================================================================

echo.
echo ====================================================================
echo          CRYPTOCURRENCY TRADING BOT - KURULUM
echo ====================================================================
echo.

REM Python kontrolu
echo [1/4] Python kontrolu yapiliyor...
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo HATA: Python bulunamadi!
    echo.
    echo Lutfen Python 3.8 veya uzeri yukleyin:
    echo https://www.python.org/downloads/
    echo.
    pause
    exit /b 1
)
python --version
echo Python bulundu! ✓
echo.

REM Paket yuklemesi
echo [2/4] Gerekli paketler yukleniyor...
echo Bu islem 2-5 dakika surebilir...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo HATA: Paket yuklemesi basarisiz!
    pause
    exit /b 1
)
echo Paketler yuklendi! ✓
echo.

REM Test
echo [3/4] Kurulum test ediliyor...
python -m pytest tests/test_core.py -v
if %ERRORLEVEL% NEQ 0 (
    echo.
    echo UYARI: Bazi testler basarisiz oldu.
    echo Bot yine de calisabilir.
)
echo Testler tamamlandi! ✓
echo.

REM Demo
echo [4/4] Demo hazir!
echo.
echo ====================================================================
echo                    KURULUM TAMAMLANDI!
echo ====================================================================
echo.
echo Simdi yapabilecekleriniz:
echo.
echo 1. Demo'yu calistir:        demo.bat
echo 2. Botu baslat:             baslat.bat
echo 3. Testleri calistir:       python -m pytest tests/test_core.py -v
echo.
echo Detayli kullanim icin NASIL_KULLANILIR.md dosyasina bakin.
echo.
pause
