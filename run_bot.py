#!/usr/bin/env python3
"""
Tarjimon Bot Ishga Tushirish Skripti
Bu skript botni oson ishga tushirish uchun yaratilgan.

"""

import os
import subprocess
import sys
import threading
import time
from pathlib import Path


def check_requirements():
    """
    Kerakli modullar o'rnatilganligini tekshirish
    """
    print("📦 Kerakli modullar tekshirilmoqda...")

    required_modules = ["telebot", "deep_translator", "requests"]

    missing_modules = []

    for module in required_modules:
        try:
            __import__(module)
            print(f"✅ {module}")
        except ImportError:
            missing_modules.append(module)
            print(f"❌ {module}")

    if missing_modules:
        print(f"\n⚠️  Quyidagi modullar topilmadi: {', '.join(missing_modules)}")
        print("📥 O'rnatish uchun quyidagi buyruqni ishga tushiring:")
        print("pip install -r requirements.txt")
        print("\nYoki:")
        print("pip install pyTelegramBotAPI deep-translator requests")

        choice = input("\n❓ Avtomatik o'rnatishni xohlaysizmi? (y/n): ").lower()
        if choice in ["y", "yes", "ha", "да"]:
            try:
                print("📥 Modullar o'rnatilmoqda...")
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"]
                )
                print("✅ Barcha modullar muvaffaqiyatli o'rnatildi!")
                return True
            except Exception as e:
                print(f"❌ O'rnatishda xatolik: {e}")
                return False
        else:
            return False

    print("✅ Barcha kerakli modullar mavjud!")
    return True


def check_bot_token():
    """
    Bot token mavjudligini tekshirish
    """
    print("\n🔑 Bot token tekshirilmoqda...")

    try:
        with open("bot.py", "r", encoding="utf-8") as f:
            content = f.read()
            if "YOUR_BOT_TOKEN_HERE" in content or 'BOT_TOKEN = ""' in content:
                print("❌ Bot token o'rnatilmagan!")
                print("\n📋 Bot token olish uchun:")
                print("1. @BotFather ga o'ting")
                print("2. /newbot buyrug'ini yuboring")
                print("3. Bot nomini va username'ini kiriting")
                print(
                    "4. Olingan tokenni bot.py faylidagi BOT_TOKEN o'zgaruvchisiga kiriting"
                )
                return False
            else:
                print("✅ Bot token mavjud!")
                return True
    except Exception as e:
        print(f"❌ bot.py faylini o'qishda xatolik: {e}")
        return False


# Web App files check removed



def get_local_ip():
    """
    Local IP manzilini olish
    """
    try:
        import socket

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "localhost"


def show_startup_info():
    """
    Ishga tushirish ma'lumotlarini ko'rsatish
    """
    local_ip = get_local_ip()

    print("\n" + "=" * 70)
    print("🚀 TARJIMON BOT")
    print("=" * 70)
    print("📱 Telegram Bot: @Transalate_uz_bot")
    print("=" * 70)
    print("🛑 To'xtatish: Ctrl+C")
    print("=" * 70)


def run_bot():
    """
    Botni ishga tushirish
    """
    try:
        print("\n📱 Telegram Bot ishga tushirilmoqda...")
        subprocess.run([sys.executable, "bot.py"])
    except KeyboardInterrupt:
        print("\n✅ Bot to'xtatildi.")
    except Exception as e:
        print(f"❌ Bot ishga tushirishda xatolik: {e}")


def main():
    """
    Asosiy funksiya
    """
    print("🤖 TARJIMON BOT STARTER")
    print("=" * 50)

    # Hozirgi papkani o'zgartirish
    script_dir = Path(__file__).parent
    os.chdir(script_dir)

    # Tekshiruvlar
    if not check_requirements():
        print("\n❌ Kerakli modullar o'rnatilmagan. Dastur to'xtatildi.")
        sys.exit(1)

    if not check_bot_token():
        print("\n❌ Bot token o'rnatilmagan. Dastur to'xtatildi.")
        sys.exit(1)

    # Web App check removed


    # Ma'lumotlarni ko'rsatish
    show_startup_info()

    # Tasdiqlash
    choice = input("\n❓ Botni ishga tushirishni xohlaysizmi? (y/n): ").lower()
    if choice not in ["y", "yes", "ha", "да"]:
        print("❌ Bekor qilindi.")
        sys.exit(0)

    # Botni ishga tushirish
    try:
        run_bot()
    except KeyboardInterrupt:
        print("\n✅ Dastur to'xtatildi.")
    except Exception as e:
        print(f"\n❌ Xatolik: {e}")


if __name__ == "__main__":
    main()
