#!/usr/bin/env python3
"""
HTTPS Setup for Telegram Web App
Bu skript ngrok orqali HTTPS URL olish va botni sozlash uchun yaratilgan.
"""

import json
import os
import subprocess
import sys
import time
import webbrowser
from pathlib import Path

try:
    import requests
except ImportError:
    print("❌ requests kutubxonasi kerak: pip install requests")
    sys.exit(1)


def print_header():
    """Header chop etish"""
    print("=" * 60)
    print("🌐 TELEGRAM WEB APP - HTTPS SETUP")
    print("=" * 60)
    print()


def check_ngrok():
    """Ngrok mavjudligini tekshirish"""
    print("🔍 Ngrok tekshirilmoqda...")
    try:
        result = subprocess.run(
            ["ngrok", "version"], capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            version = result.stdout.strip().split("\n")[0]
            print(f"✅ Ngrok topildi: {version}")
            return True
    except (FileNotFoundError, subprocess.TimeoutExpired):
        pass

    print("❌ Ngrok topilmadi!")
    return False


def install_ngrok_guide():
    """Ngrok o'rnatish yo'riqnomasi"""
    print()
    print("📦 NGROK O'RNATISH:")
    print("-" * 30)
    print("1. https://ngrok.com saytiga o'ting")
    print("2. Sign up qiling (bepul)")
    print("3. Download tugmasini bosing")
    print("4. Windows uchun ngrok.exe ni yuklab oling")
    print("5. ngrok.exe ni C:\\Windows\\ yoki loyiha papkasiga qo'ying")
    print("6. Dashboard'dan authtoken ni oling")
    print("7. ngrok config add-authtoken <TOKEN>")
    print()

    choice = input("❓ Ngrok o'rnatdingizmi? (y/n): ").lower()
    return choice in ["y", "yes", "ha"]


def setup_ngrok_auth():
    """Ngrok authtoken sozlash"""
    print()
    print("🔑 NGROK AUTHTOKEN SETUP:")
    print("-" * 30)
    print("1. https://dashboard.ngrok.com/get-started/your-authtoken")
    print("2. Token ni nusxalang")
    print()

    token = input("📝 Authtoken kiriting (Enter - o'tkazib yuborish): ").strip()

    if not token:
        print("⏭️  Token o'tkazib yuborildi")
        return True

    try:
        result = subprocess.run(
            ["ngrok", "config", "add-authtoken", token],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode == 0:
            print("✅ Authtoken saqlandi!")
            return True
        else:
            print(f"❌ Xatolik: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Authtoken sozlashda xatolik: {e}")
        return False


def start_local_server():
    """Local flask serverni tekshirish"""
    print()
    print("🌐 Local server tekshirilmoqda...")

    try:
        response = requests.get("http://localhost:5000", timeout=3)
        if response.status_code == 200:
            print("✅ Local server (localhost:5000) ishlayapti")
            return True
    except:
        pass

    print("❌ Local server ishlamayapti")
    print("💡 Avval 'python bot.py' ni ishga tushiring")
    return False


def create_ngrok_tunnel():
    """Ngrok tunnel yaratish"""
    print()
    print("🚀 Ngrok tunnel yaratilmoqda...")

    # Eski tunnel'larni to'xtatish
    try:
        # Windows'da taskkill, Linux/Mac'da pkill
        if os.name == "nt":
            subprocess.run(
                ["taskkill", "/f", "/im", "ngrok.exe"], capture_output=True, check=False
            )
        else:
            subprocess.run(["pkill", "-f", "ngrok"], capture_output=True, check=False)
        time.sleep(1)
    except:
        pass

    try:
        # Ngrok'ni background'da ishga tushirish
        if os.name == "nt":
            # Windows
            process = subprocess.Popen(
                ["ngrok", "http", "5000", "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                creationflags=subprocess.CREATE_NEW_CONSOLE,
            )
        else:
            # Linux/Mac
            process = subprocess.Popen(
                ["ngrok", "http", "5000", "--log=stdout"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )

        print("⏳ Tunnel ishga tushmoqda...")
        time.sleep(3)

        # Tunnel URL'ni olish
        return get_tunnel_url(), process

    except Exception as e:
        print(f"❌ Ngrok ishga tushmadi: {e}")
        return None, None


def get_tunnel_url():
    """Ngrok API orqali URL olish"""
    try:
        response = requests.get("http://127.0.0.1:4040/api/tunnels", timeout=5)

        if response.status_code == 200:
            data = response.json()
            tunnels = data.get("tunnels", [])

            for tunnel in tunnels:
                if tunnel.get("proto") == "https":
                    url = tunnel.get("public_url")
                    if url:
                        print(f"✅ HTTPS URL topildi: {url}")
                        return url

        print("⚠️  API orqali URL olinmadi")
        return None

    except Exception as e:
        print(f"⚠️  URL olishda xatolik: {e}")
        return None


def update_bot_code(https_url):
    """Bot kodini yangilash"""
    print()
    print("🔄 Bot kodi yangilanmoqda...")

    bot_file = Path("bot.py")
    if not bot_file.exists():
        print("❌ bot.py fayli topilmadi!")
        return False

    try:
        # Faylni o'qish
        content = bot_file.read_text(encoding="utf-8")

        # URL'larni almashtirish
        replacements = [
            ("http://localhost:5000", https_url),
            ("https://localhost:5000", https_url),
        ]

        for old, new in replacements:
            content = content.replace(old, new)

        # Web App tugmasini yoqish
        # Disable qilingan qismni topib, enable qilish
        if "web_app=types.WebAppInfo(url=" in content:
            print("✅ Web App tugmasi allaqachon faol")
        else:
            # Web App tugmasini qo'shish kodi
            start_marker = "# Web App tugmasi vaqtincha o'chirildi"
            if start_marker in content:
                # Eski kodni almashtirish
                old_code = """    # Web App tugmasi vaqtincha o'chirildi (HTTPS kerak)
    # Production uchun GitHub Pages yoki ngrok ishlatilishi kerak
    welcome_text += (
        "\\n\\n💡 **Web App:** http://localhost:5000 brauzerda ochiladi\\n"
        "📱 **Telegram integratsiyasi:** GitHub Pages orqali"
    )
    bot.reply_to(message, welcome_text, parse_mode="Markdown")"""

                new_code = f'''    # Web App tugmasi (HTTPS URL bilan)
    keyboard = types.InlineKeyboardMarkup()
    webapp_button = types.InlineKeyboardButton(
        "🌐 Web App'da ochish",
        web_app=types.WebAppInfo(url="{https_url}")
    )
    keyboard.add(webapp_button)
    bot.reply_to(message, welcome_text, reply_markup=keyboard)'''

                content = content.replace(old_code, new_code)
                print("✅ Web App tugmasi yoqildi")
            else:
                print("⚠️  Web App tugmasi kodi topilmadi")

        # Faylni saqlash
        bot_file.write_text(content, encoding="utf-8")
        print("✅ bot.py yangilandi!")
        return True

    except Exception as e:
        print(f"❌ Fayl yangilashda xatolik: {e}")
        return False


def create_start_script(https_url):
    """Ishga tushirish skripti yaratish"""
    print()
    print("📝 Start skripti yaratilmoqda...")

    batch_content = f"""@echo off
title Tarjimon Bot + Web App (NGROK)
color 0A

echo.
echo ================================================================
echo               TARJIMON BOT + WEB APP (NGROK)
echo ================================================================
echo.
echo 📱 Bot: @Transalate_uz_bot
echo 🌐 Web App: {https_url}
echo 🔧 Ngrok: http://127.0.0.1:4040 (dashboard)
echo.
echo ================================================================
echo.

echo 🌐 Ngrok tunnel ishga tushirilmoqda...
start /B ngrok http 5000

echo ⏳ 5 soniya kutilmoqda...
timeout /t 5 /nobreak >nul

echo 📱 Bot ishga tushirilmoqda...
python bot.py

echo.
echo Bot to'xtatildi. Ngrok ham to'xtatilsinmi?
pause

echo 🛑 Ngrok to'xtatilmoqda...
taskkill /f /im ngrok.exe 2>nul

echo.
echo ✅ Hammasi to'xtatildi
pause
"""

    try:
        with open("start_with_ngrok.bat", "w", encoding="utf-8") as f:
            f.write(batch_content)
        print("✅ start_with_ngrok.bat yaratildi!")
        return True
    except Exception as e:
        print(f"❌ Batch fayl yaratishda xatolik: {e}")
        return False


def main():
    """Asosiy funksiya"""
    print_header()

    # 1. Ngrok tekshirish
    if not check_ngrok():
        if not install_ngrok_guide():
            print("❌ Ngrok o'rnatmasdan davom etib bo'lmaydi")
            return

        # Qayta tekshirish
        if not check_ngrok():
            print("❌ Ngrok hali ham topilmadi!")
            return

    # 2. Local server tekshirish
    if not start_local_server():
        choice = input("❓ Bot'ni ishga tushirmasdan davom etamizmi? (y/n): ").lower()
        if choice not in ["y", "yes", "ha"]:
            print(
                "💡 Avval 'python bot.py' ni ishga tushiring, keyin qaytadan urinib ko'ring"
            )
            return

    # 3. Ngrok auth setup
    if not setup_ngrok_auth():
        print("⚠️  Authtoken o'tkazib yuborildi, cheklangan funksionallik")

    # 4. Ngrok tunnel yaratish
    https_url, process = create_ngrok_tunnel()

    if not https_url:
        print("❌ HTTPS URL olinmadi")
        print("🔧 Manual setup:")
        print("1. http://127.0.0.1:4040 ochib HTTPS URL ni ko'ring")
        print("2. Bot kodida URL'ni qo'lda almashtiring")
        return

    # 5. Bot kodni yangilash
    if not update_bot_code(https_url):
        print("⚠️  Bot kodi yangilanmadi, qo'lda o'zgartiring")
        print(f"🔗 Yangi URL: {https_url}")
        return

    # 6. Start skript yaratish
    create_start_script(https_url)

    # 7. Yakuniy ma'lumotlar
    print()
    print("=" * 60)
    print("🎉 MUVAFFAQIYAT!")
    print("=" * 60)
    print(f"🌐 HTTPS URL: {https_url}")
    print(f"🔧 Ngrok dashboard: http://127.0.0.1:4040")
    print(f"📱 Telegram bot: @Transalate_uz_bot")
    print("=" * 60)
    print()
    print("🚀 KEYINGI QADAMLAR:")
    print("1. Bot'ni qayta ishga tushiring: python bot.py")
    print("2. Telegram'da /start buyrug'ini yuboring")
    print("3. '🌐 Web App'da ochish' tugmasini bosing")
    print()
    print("💾 Keyingi safar: start_with_ngrok.bat ishlatng")
    print("🌍 Ngrok dashboard: http://127.0.0.1:4040")
    print()

    # Browser ochish
    choice = input("❓ Ngrok dashboard'ni ochishni xohlaysizmi? (y/n): ").lower()
    if choice in ["y", "yes", "ha"]:
        webbrowser.open("http://127.0.0.1:4040")

    print()
    print("✨ Setup yakunlandi!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Foydalanuvchi tomonidan bekor qilindi")
    except Exception as e:
        print(f"\n\n❌ Kutilmagan xatolik: {e}")
    finally:
        print("\n🔚 Setup tugadi")
