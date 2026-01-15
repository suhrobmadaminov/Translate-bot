#!/usr/bin/env python3
"""
Ngrok Setup Script for Telegram Web App
Bu skript ngrok orqali HTTPS URL olish va botni sozlash uchun yaratilgan.
"""

import json
import os
import subprocess
import sys
import time
from pathlib import Path

import requests


def check_ngrok_installed():
    """
    Ngrok o'rnatilganligini tekshirish
    """
    print("🔍 Ngrok tekshirilmoqda...")
    try:
        result = subprocess.run(["ngrok", "version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Ngrok topildi: {result.stdout.strip()}")
            return True
    except FileNotFoundError:
        pass

    print("❌ Ngrok topilmadi!")
    return False


def install_ngrok_instructions():
    """
    Ngrok o'rnatish yo'riqnomasi
    """
    print("\n📦 NGROK O'RNATISH YO'RIQNOMASI:")
    print("=" * 50)
    print("1. https://ngrok.com/ saytiga o'ting")
    print("2. 'Download' tugmasini bosing")
    print("3. Windows uchun zip faylni yuklab oling")
    print(
        "4. Zip'ni ochib, ngrok.exe faylni C:\\Windows\\System32 papkasiga ko'chiring"
    )
    print("   (yoki PATH'ga qo'shing)")
    print("5. Ngrok.com'da ro'yxatdan o'ting (bepul)")
    print("6. Dashboard'dan authtoken ni oling")
    print("7. Terminal'da: ngrok config add-authtoken <YOUR_TOKEN>")
    print("\n💡 Yoki portable ishlatish uchun:")
    print("   - ngrok.exe ni loyiha papkasiga ko'chiring")
    print("   - ./ngrok.exe buyrug'ini ishlating")
    print("=" * 50)


def get_ngrok_token():
    """
    Ngrok token olish
    """
    print("\n🔑 Ngrok authtoken sozlash:")
    print("1. https://dashboard.ngrok.com/get-started/your-authtoken saytiga o'ting")
    print("2. Token ni nusxalang")

    token = input(
        "\n📝 Authtoken ni kiriting (bo'sh qoldirsa o'tkazib yuboriladi): "
    ).strip()

    if token:
        try:
            result = subprocess.run(
                ["ngrok", "config", "add-authtoken", token],
                capture_output=True,
                text=True,
            )
            if result.returncode == 0:
                print("✅ Token muvaffaqiyatli qo'shildi!")
                return True
            else:
                print(f"❌ Token qo'shishda xatolik: {result.stderr}")
        except Exception as e:
            print(f"❌ Token sozlashda xatolik: {e}")

    return False


def start_ngrok_tunnel():
    """
    Ngrok tunnel'ni ishga tushirish
    """
    print("\n🌐 Ngrok tunnel yaratilmoqda...")

    # Ngrok tunnel'ni background'da ishga tushirish
    try:
        # Avval mavjud tunnel'larni to'xtatish
        try:
            subprocess.run(["pkill", "-f", "ngrok"], check=False)
        except:
            pass

        # Yangi tunnel ishga tushirish
        process = subprocess.Popen(
            ["ngrok", "http", "5000", "--log=stdout"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )

        # Bir oz kutish tunnel ishga tushishi uchun
        time.sleep(3)

        # Tunnel URL'ni olish
        try:
            response = requests.get("http://127.0.0.1:4040/api/tunnels")
            if response.status_code == 200:
                data = response.json()
                tunnels = data.get("tunnels", [])

                for tunnel in tunnels:
                    if tunnel.get("proto") == "https":
                        public_url = tunnel.get("public_url")
                        if public_url:
                            print(f"✅ HTTPS URL: {public_url}")
                            return public_url, process

        except Exception as e:
            print(f"⚠️  API orqali URL olishda xatolik: {e}")

        print("⚠️  Tunnel yaratildi, lekin URL avtomatik olinmadi")
        print("🌐 http://127.0.0.1:4040 ga o'tib, HTTPS URL'ni qo'lda oling")
        return None, process

    except Exception as e:
        print(f"❌ Ngrok tunnel yaratishda xatolik: {e}")
        return None, None


def update_bot_urls(https_url):
    """
    Bot faylidagi URL'larni yangilash
    """
    if not https_url:
        return False

    print(f"\n🔄 Bot fayli yangilan moqda: {https_url}")

    try:
        bot_file = Path("bot.py")
        if not bot_file.exists():
            print("❌ bot.py fayli topilmadi!")
            return False

        # Faylni o'qish
        content = bot_file.read_text(encoding="utf-8")

        # URL'larni almashtirish
        old_patterns = [
            "http://localhost:5000",
            "https://your-domain.com",
            "https://localhost:5000",
        ]

        for pattern in old_patterns:
            content = content.replace(pattern, https_url)

        # Faylni saqlash
        bot_file.write_text(content, encoding="utf-8")
        print("✅ Bot fayli yangilandi!")
        return True

    except Exception as e:
        print(f"❌ Bot faylini yangilashda xatolik: {e}")
        return False


def create_start_script(https_url):
    """
    Ishga tushirish skripti yaratish
    """
    if not https_url:
        return

    script_content = f"""@echo off
echo 🚀 TARJIMON BOT + WEB APP (NGROK)
echo ================================
echo 📱 Bot: @Transalate_uz_bot
echo 🌐 Web App: {https_url}
echo ================================
echo.

echo 🌐 Ngrok tunnel ishlamoqda...
start /B ngrok http 5000

echo ⏳ 3 soniya kutilmoqda...
timeout /t 3 /nobreak >nul

echo 📱 Bot ishga tushirilmoqda...
python bot.py

pause
"""

    try:
        with open("start_with_ngrok.bat", "w", encoding="utf-8") as f:
            f.write(script_content)
        print("✅ start_with_ngrok.bat yaratildi!")
        print("💡 Keyingi safar faqat start_with_ngrok.bat ni ishga tushiring")
    except Exception as e:
        print(f"❌ Batch fayl yaratishda xatolik: {e}")


def main():
    """
    Asosiy funksiya
    """
    print("🌐 NGROK SOZLASH VA TELEGRAM WEB APP")
    print("=" * 50)

    # Ngrok tekshirish
    if not check_ngrok_installed():
        install_ngrok_instructions()

        choice = input("\n❓ Ngrok o'rnatdingizmi? Davom etamizmi? (y/n): ").lower()
        if choice not in ["y", "yes", "ha"]:
            print("❌ Ngrok o'rnatib, qayta urinib ko'ring.")
            return

        # Qayta tekshirish
        if not check_ngrok_installed():
            print("❌ Ngrok hali ham topilmadi!")
            return

    # Token sozlash
    get_ngrok_token()

    # Tunnel yaratish
    https_url, process = start_ngrok_tunnel()

    if https_url:
        print(f"\n🎉 Muvaffaqiyat! HTTPS URL: {https_url}")

        # Bot faylini yangilash
        if update_bot_urls(https_url):
            create_start_script(https_url)

            print(f"\n✅ HAMMASI TAYYOR!")
            print("=" * 50)
            print(f"🌐 Sizning Web App URL: {https_url}")
            print("📱 Bot: @Transalate_uz_bot")
            print("=" * 50)
            print("\n🚀 Ishga tushirish:")
            print("1. Yangi terminal oching")
            print("2. python bot.py ni ishga tushiring")
            print("3. Telegram'da /webapp buyrug'ini yuboring")
            print("\n💡 Yoki start_with_ngrok.bat ni ishga tushiring")

            choice = input("\n❓ Hoziroq botni ishga tushiramizmi? (y/n): ").lower()
            if choice in ["y", "yes", "ha"]:
                print("\n🚀 Bot ishga tushirilmoqda...")
                try:
                    subprocess.run([sys.executable, "bot.py"])
                except KeyboardInterrupt:
                    print("\n✅ Bot to'xtatildi.")
                finally:
                    if process:
                        process.terminate()
        else:
            print("⚠️  Bot faylini qo'lda yangilang:")
            print(f"   http://localhost:5000 → {https_url}")

    else:
        print("\n⚠️  Ngrok tunnel yaratildi, lekin URL avtomatik olinmadi")
        print("🔧 Qo'lda sozlash:")
        print("1. http://127.0.0.1:4040 saytiga o'ting")
        print("2. HTTPS URL'ni nusxalang")
        print("3. bot.py faylidagi http://localhost:5000 ni yangi URL ga almashtiring")
        print("4. Bot'ni ishga tushiring")


if __name__ == "__main__":
    main()
