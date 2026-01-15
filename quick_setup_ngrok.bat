@echo off
title Ngrok Quick Setup for Telegram Web App
color 0A
cls

echo.
echo ================================================================
echo              NGROK QUICK SETUP - TELEGRAM WEB APP
echo ================================================================
echo.

REM Check if ngrok is installed
ngrok version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Ngrok topilmadi!
    echo.
    echo 📦 NGROK O'RNATISH:
    echo 1. https://ngrok.com saytiga o'ting
    echo 2. Sign up qiling ^(bepul^)
    echo 3. Download ^> Windows ^> ngrok.exe yuklab oling
    echo 4. ngrok.exe ni shu papkaga qo'ying yoki PATH ga qo'shing
    echo 5. Dashboard dan authtoken ni oling
    echo 6. ngrok config add-authtoken ^<TOKEN^>
    echo.
    pause
    exit /b 1
)

echo ✅ Ngrok topildi
echo.

REM Check if bot is running
echo 🔍 Local server tekshirilmoqda...
curl -s http://localhost:5000 >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Bot ishlamayapti!
    echo.
    echo 💡 Avval botni ishga tushiring:
    echo    python bot.py
    echo.
    echo Keyin qaytadan bu skriptni ishga tushiring.
    echo.
    pause
    exit /b 1
)

echo ✅ Local server ishlayapti ^(localhost:5000^)
echo.

REM Kill existing ngrok processes
echo 🛑 Eski ngrok jarayonlarini to'xtatish...
taskkill /f /im ngrok.exe >nul 2>&1

echo 🚀 Ngrok tunnel yaratilmoqda...
echo.

REM Start ngrok in background
start /B ngrok http 5000

echo ⏳ 5 soniya kutilmoqda tunnel ishga tushishi uchun...
timeout /t 5 /nobreak >nul

echo.
echo 🔍 HTTPS URL ni qidirilmoqda...

REM Try to get the URL via API
curl -s http://127.0.0.1:4040/api/tunnels > temp_tunnels.json 2>nul

if exist temp_tunnels.json (
    REM Extract HTTPS URL using findstr (basic parsing)
    for /f "tokens=*" %%i in ('findstr "https.*ngrok" temp_tunnels.json') do (
        set "line=%%i"
        goto found_url
    )

    :found_url
    REM Clean up the URL (remove quotes and extra characters)
    for /f "tokens=2 delims=:, " %%j in ('findstr "https.*ngrok" temp_tunnels.json') do (
        set "url=%%j"
        set "url=!url:"=!"
        set "url=!url: =!"
        if "!url:~0,5!"=="https" (
            set "HTTPS_URL=!url!"
            goto url_found
        )
    )

    :url_found
    del temp_tunnels.json >nul 2>&1
)

if defined HTTPS_URL (
    echo ✅ HTTPS URL topildi: %HTTPS_URL%
    echo.

    REM Update bot.py file
    echo 🔄 Bot fayli yangilanmoqda...

    REM Create a temp PowerShell script to update the file
    echo $content = Get-Content 'bot.py' -Raw > update_bot.ps1
    echo $content = $content -replace 'http://localhost:5000', '%HTTPS_URL%' >> update_bot.ps1
    echo $content = $content -replace 'https://localhost:5000', '%HTTPS_URL%' >> update_bot.ps1
    echo Set-Content 'bot.py' -Value $content >> update_bot.ps1

    powershell -ExecutionPolicy Bypass -File update_bot.ps1 >nul 2>&1
    del update_bot.ps1 >nul 2>&1

    echo ✅ Bot fayli yangilandi!
    echo.

    echo ================================================================
    echo                        🎉 TAYYOR! 🎉
    echo ================================================================
    echo.
    echo 🌐 Sizning HTTPS URL: %HTTPS_URL%
    echo 🔧 Ngrok Dashboard: http://127.0.0.1:4040
    echo 📱 Bot: @Transalate_uz_bot
    echo.
    echo ================================================================
    echo.
    echo 🚀 KEYINGI QADAMLAR:
    echo 1. Botni qayta ishga tushiring: python bot.py
    echo 2. Telegram da /start buyrug'ini yuboring
    echo 3. "🌐 Web App'da ochish" tugmasini bosing
    echo 4. Web App Telegram ichida ochiladi!
    echo.
    echo 💡 ESLATMA: Ngrok tunnel 8 soat faol bo'ladi
    echo.
    echo ================================================================

    set /p restart="❓ Hoziroq botni qayta ishga tushiramizmi? (y/n): "
    if /i "!restart!"=="y" (
        echo.
        echo 🔄 Bot qayta ishga tushirilmoqda...
        python bot.py
    )

) else (
    echo ❌ HTTPS URL avtomatik olinmadi
    echo.
    echo 🔧 MANUAL SETUP:
    echo 1. http://127.0.0.1:4040 saytini oching
    echo 2. HTTPS URL ni ko'ring ^(https://xxxxx.ngrok.io^)
    echo 3. Bot.py faylidagi http://localhost:5000 ni yangi URL ga almashtiring
    echo 4. Botni qayta ishga tushiring
    echo.

    set /p open_dashboard="❓ Ngrok dashboard ni ochishni xohlaysizmi? (y/n): "
    if /i "!open_dashboard!"=="y" (
        start http://127.0.0.1:4040
    )
)

echo.
echo 🔚 Setup tugadi!
pause
