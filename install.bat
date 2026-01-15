@echo off
title Tarjimon Bot - Dependencies Installer
color 0B
cls

echo.
echo ================================================================
echo           TARJIMON BOT - KUTUBXONALAR O'RNATISH
echo ================================================================
echo.

REM Check Python
echo [1/4] Python tekshirilmoqda...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python topilmadi!
    echo.
    echo Python o'rnatish:
    echo 1. https://python.org saytiga o'ting
    echo 2. Python 3.8+ ni yuklab oling
    echo 3. O'rnatishda "Add Python to PATH" ni belgilang
    echo 4. Kompyuterni qayta ishga tushiring
    echo.
    pause
    exit /b 1
)
echo ✅ Python mavjud

REM Check pip
echo.
echo [2/4] pip tekshirilmoqda...
pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ pip topilmadi!
    echo.
    echo pip ni qayta o'rnatish:
    echo python -m ensurepip --upgrade
    echo.
    pause
    exit /b 1
)
echo ✅ pip mavjud

REM Install requirements
echo.
echo [3/4] Kutubxonalar o'rnatilmoqda...
echo.
echo 📦 O'rnatilayotgan kutubxonalar:
echo   - pyTelegramBotAPI==4.14.0 (Telegram Bot)
echo   - deep-translator==1.11.4 (Tarjima)
echo   - Flask==2.3.3 (Web App)
echo   - Werkzeug==2.3.7 (Flask dependency)
echo   - requests==2.31.0 (HTTP requests)
echo.

pip install pyTelegramBotAPI==4.14.0
if %errorlevel% neq 0 (
    echo ❌ pyTelegramBotAPI o'rnatilmadi
    goto ERROR
)
echo ✅ pyTelegramBotAPI o'rnatildi

pip install deep-translator==1.11.4
if %errorlevel% neq 0 (
    echo ❌ deep-translator o'rnatilmadi
    goto ERROR
)
echo ✅ deep-translator o'rnatildi

pip install Flask==2.3.3
if %errorlevel% neq 0 (
    echo ❌ Flask o'rnatilmadi
    goto ERROR
)
echo ✅ Flask o'rnatildi

pip install Werkzeug==2.3.7
if %errorlevel% neq 0 (
    echo ❌ Werkzeug o'rnatilmadi
    goto ERROR
)
echo ✅ Werkzeug o'rnatildi

pip install requests==2.31.0
if %errorlevel% neq 0 (
    echo ❌ requests o'rnatilmadi
    goto ERROR
)
echo ✅ requests o'rnatildi

REM Verify installation
echo.
echo [4/4] O'rnatish tekshirilmoqda...
python -c "import telebot; print('✅ telebot')" 2>nul || echo ❌ telebot
python -c "import deep_translator; print('✅ deep_translator')" 2>nul || echo ❌ deep_translator
python -c "import flask; print('✅ flask')" 2>nul || echo ❌ flask
python -c "import werkzeug; print('✅ werkzeug')" 2>nul || echo ❌ werkzeug
python -c "import requests; print('✅ requests')" 2>nul || echo ❌ requests

echo.
echo ================================================================
echo                    🎉 MUVAFFAQIYAT! 🎉
echo ================================================================
echo.
echo ✅ Barcha kutubxonalar muvaffaqiyatli o'rnatildi!
echo.
echo 📋 Keyingi qadamlar:
echo 1. bot.py faylida BOT_TOKEN ni sozlang
echo 2. START_BOT.bat ni ishga tushiring
echo 3. Yoki: python bot.py
echo.
echo 💡 Bot token olish:
echo   - @BotFather ga o'ting
echo   - /newbot buyrug'ini yuboring
echo   - Token ni bot.py ga joylashtiring
echo.
echo ================================================================
pause
exit /b 0

:ERROR
echo.
echo ================================================================
echo                      ❌ XATOLIK!
echo ================================================================
echo.
echo Ba'zi kutubxonalar o'rnatilmadi.
echo.
echo 🔧 Muammolarni hal qilish:
echo.
echo 1. Internet aloqasini tekshiring
echo 2. Python va pip versiyasini tekshiring:
echo    python --version
echo    pip --version
echo.
echo 3. pip ni yangilang:
echo    python -m pip install --upgrade pip
echo.
echo 4. Proxy yoki firewall muammosini tekshiring
echo.
echo 5. Qo'lda o'rnatib ko'ring:
echo    pip install -r requirements.txt
echo.
echo 6. Virtual environment ishlatib ko'ring:
echo    python -m venv venv
echo    venv\Scripts\activate
echo    pip install -r requirements.txt
echo.
echo ================================================================
pause
exit /b 1
