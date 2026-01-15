@echo off
title Tarjimon Bot + Web App Starter
color 0A
echo.
echo ===============================================================
echo                 TARJIMON BOT + WEB APP STARTER
echo ===============================================================
echo.
echo Bot: @Transalate_uz_bot
echo Web App: Chiroyli interfeys bilan
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ❌ Python topilmadi!
    echo.
    echo Python o'rnatish:
    echo 1. https://python.org saytiga o'ting
    echo 2. Python 3.8+ ni yuklab oling
    echo 3. O'rnatishda "Add to PATH" ni belgilang
    echo.
    pause
    exit /b 1
)

echo ✅ Python mavjud
echo.

REM Check if bot.py exists
if not exist "bot.py" (
    echo ❌ bot.py fayli topilmadi!
    echo.
    echo Iltimos, skriptni to'g'ri papkada ishga tushiring.
    echo.
    pause
    exit /b 1
)

echo ✅ bot.py fayli mavjud
echo.

REM Install requirements
echo 📦 Kerakli kutubxonalar tekshirilmoqda...
pip install pyTelegramBotAPI==4.14.0 deep-translator==1.11.4 Flask==2.3.3 >nul 2>&1

if %errorlevel% neq 0 (
    echo ⚠️  Ba'zi kutubxonlar o'rnatilmagan bo'lishi mumkin
    echo 💡 Internet aloqasini tekshiring
    echo.
) else (
    echo ✅ Barcha kutubxonalar tayyor
    echo.
)

REM Show menu
:MENU
echo ===============================================================
echo                          TANLOV MENYUSI
echo ===============================================================
echo.
echo 1. 🚀 Bot + Web App ni ishga tushirish (localhost)
echo 2. 📱 Faqat Bot'ni ishga tushirish
echo 3. 🌐 Faqat Web App'ni ishga tushirish (test)
echo 4. ⚙️  Bot tokenini tekshirish
echo 5. 🌍 GitHub Pages setup yo'riqnomasi
echo 6. 📚 Yordam va dokumentatsiya
echo 0. ❌ Chiqish
echo.
set /p choice="Tanlovingizni kiriting (0-6): "

if "%choice%"=="1" goto START_FULL
if "%choice%"=="2" goto START_BOT_ONLY
if "%choice%"=="3" goto START_WEBAPP_ONLY
if "%choice%"=="4" goto CHECK_TOKEN
if "%choice%"=="5" goto GITHUB_GUIDE
if "%choice%"=="6" goto HELP
if "%choice%"=="0" goto EXIT
goto MENU

:START_FULL
cls
echo ===============================================================
echo              🚀 BOT + WEB APP ISHGA TUSHIRILMOQDA
echo ===============================================================
echo.
echo 📱 Telegram Bot: @Transalate_uz_bot
echo 🌐 Web App: http://localhost:5000
echo ⚡ Test uchun: http://localhost:5000/test.html
echo.
echo ⏳ Ishga tushirilmoqda...
echo 🛑 To'xtatish: Ctrl+C
echo.
echo ===============================================================
echo.
python bot.py
goto END

:START_BOT_ONLY
cls
echo ===============================================================
echo                   📱 FAQAT BOT ISHGA TUSHIRILDI
echo ===============================================================
echo.
echo Bot: @Transalate_uz_bot
echo.
echo Web App funksiyasi mavjud emas (faqat bot buyruqlari)
echo.
echo ⏳ Ishga tushirilmoqda...
echo 🛑 To'xtatish: Ctrl+C
echo.
echo ===============================================================
echo.
REM Set environment variable to disable webapp
set DISABLE_WEBAPP=1
python bot.py
goto END

:START_WEBAPP_ONLY
cls
echo ===============================================================
echo                 🌐 FAQAT WEB APP TEST SERVERI
echo ===============================================================
echo.
echo 🏠 Local: http://localhost:5000
echo 📱 Test: http://localhost:5000/test.html
echo.
echo 💡 Bu test server - haqiqiy tarjima yo'q
echo 🔗 Haqiqiy tarjima uchun bot kerak
echo.
echo ⏳ Ishga tushirilmoqda...
echo 🛑 To'xtatish: Ctrl+C
echo.
echo ===============================================================
echo.
python local_webapp.py
goto END

:CHECK_TOKEN
cls
echo ===============================================================
echo                     🔑 BOT TOKEN TEKSHIRUVI
echo ===============================================================
echo.
findstr "BOT_TOKEN.*=" bot.py | findstr -v "YOUR_BOT_TOKEN_HERE"
if %errorlevel% equ 0 (
    echo ✅ Bot token sozlangan ko'rinadi
    echo.
    echo 💡 Token'ni to'liq tekshirish uchun bot'ni ishga tushiring
) else (
    echo ❌ Bot token sozlanmagan!
    echo.
    echo 📝 Bot token sozlash:
    echo 1. @BotFather ga o'ting
    echo 2. /newbot buyrug'ini yuboring
    echo 3. Bot nomi va username kiriting
    echo 4. Olingan tokenni bot.py faylidagi BOT_TOKEN ga yozing
    echo.
    echo Fayl: bot.py
    echo Qator: BOT_TOKEN = "BU_YERGA_TOKEN"
)
echo.
echo ===============================================================
pause
goto MENU

:GITHUB_GUIDE
cls
echo ===============================================================
echo                   🌍 GITHUB PAGES SETUP
echo ===============================================================
echo.
echo GitHub Pages orqali BEPUL Web App hosting:
echo.
echo 📋 Qadamlar:
echo 1. GitHub.com da yangi repository yarating
echo 2. Repository'ni public qiling
echo 3. webapp/ papkasidagi fayllarni yuklang:
echo    - index.html
echo    - static/css/style.css
echo    - static/js/app.js
echo.
echo 4. Repository Settings ^> Pages
echo 5. Source: "Deploy from a branch"
echo 6. Branch: "main", Folder: "/ (root)"
echo 7. Save tugmasini bosing
echo.
echo 8. Sizning URL: https://USERNAME.github.io/REPO-NAME/
echo 9. Bot faylidagi URL ni yangilang
echo.
echo 📚 Batafsil yo'riqnoma: DEPLOY_GITHUB.md faylida
echo.
echo ===============================================================
pause
goto MENU

:HELP
cls
echo ===============================================================
echo                      📚 YORDAM VA MA'LUMOT
echo ===============================================================
echo.
echo 🤖 TELEGRAM BOT:
echo - Bot: @Transalate_uz_bot
echo - Buyruqlar: /start, /help, /webapp, /translate
echo - Inline mode: @bot_username matn
echo.
echo 🌐 WEB APP:
echo - Local test: http://localhost:5000
echo - Production: GitHub Pages
echo - Telegram Web App integration
echo.
echo 📁 FAYLLAR:
echo - bot.py - Asosiy bot kodi
echo - webapp/ - Web App fayllari
echo - requirements.txt - Python dependencies
echo - DEPLOY_GITHUB.md - GitHub Pages guide
echo.
echo 🔧 TEXNIK:
echo - Python 3.8+
echo - Flask web server
echo - Telegram Bot API
echo - Google Translate API
echo.
echo 🆘 YORDAM:
echo - README.md faylini o'qing
echo - Bot loglarini tekshiring
echo - Internet aloqasini tasdiqlang
echo.
echo ===============================================================
pause
goto MENU

:EXIT
echo.
echo ===============================================================
echo                          XAYR!
echo ===============================================================
echo.
echo Tarjimon Bot'dan foydalanganingiz uchun rahmat! 🙏
echo.
echo 📞 Savollar bo'lsa:
echo - README.md ni o'qing
echo - GitHub'da issue yarating
echo - Bot: @Transalate_uz_bot
echo.
echo 🌟 Bot'ni do'stlaringiz bilan ulashing!
echo.
echo ===============================================================
timeout /t 3 /nobreak >nul
exit /b 0

:END
echo.
echo ===============================================================
echo                     DASTUR YAKUNLANDI
echo ===============================================================
echo.
echo 💡 Qayta ishga tushirish uchun: START_BOT.bat
echo 🔄 Yangi funktsiyalar uchun: git pull
echo 📚 Yordam uchun: README.md
echo.
pause
goto MENU
