"""
Telegram Tarjimon Bot
Bu bot foydalanuvchilarga matnlarni turli tillarga tarjima qilish imkoniyatini beradi.
"""

import json
import logging
import os
import signal
import sys
import threading
import time
from datetime import datetime

import telebot
from deep_translator import GoogleTranslator
from telebot import types

from dotenv import load_dotenv

# .env faylidan o'zgaruvchilarni yuklash
load_dotenv()

# Bot tokenini muhit o'zgaruvchilaridan olish
BOT_TOKEN = os.getenv("BOT_TOKEN", "8543153606:AAH3_nB0HShneekrtpU3sjyNJMMA_1XqB8Y")

# Admin sozlamalari
ADMIN_ID = os.getenv("ADMIN_ID") # Masalan: 12345678
if ADMIN_ID:
    try:
        ADMIN_ID = int(ADMIN_ID)
    except ValueError:
        ADMIN_ID = None

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "MadaminovSuhrob")


# Bot va tarjimon obyektlarini yaratish
try:
    bot = telebot.TeleBot(BOT_TOKEN)
    print("Bot va tarjimon obyektlari yaratildi.")
except Exception as e:
    print(f"Bot yaratishda xatolik: {e}")
    sys.exit(1)


def is_admin(user):
    """Foydalanuvchi admin ekanligini tekshirish"""
    if ADMIN_ID and user.id == ADMIN_ID:
        return True
    if ADMIN_USERNAME and user.username == ADMIN_USERNAME:
        return True
    return False


# Logging sozlamalari (xatolarni kuzatish uchun)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Foydalanuvchilar matnlarini saqlash (user_id -> text)
user_texts = {}

# Statistika (user_id -> count)
user_stats = {}

# Favorit tillar (user_id -> [lang_codes])
favorite_languages = {}

# Tarjima tarixi (user_id -> [history_items])
translation_history = {}

# Foydalanuvchi sozlamalari (user_id -> settings)
user_settings = {}

# Fayllar saqlash papkasi
FILES_DIR = "translated_files"
if not os.path.exists(FILES_DIR):
    os.makedirs(FILES_DIR)

# Foydalanuvchilar bazasi (file)
USERS_FILE = "users.json"
connected_users = set()

def load_users():
    """Foydalanuvchilarni fayldan yuklash"""
    global connected_users
    if os.path.exists(USERS_FILE):
        try:
            with open(USERS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                connected_users = set(data.get("users", []))
        except Exception as e:
            print(f"Error loading users: {e}")

def save_users():
    """Foydalanuvchilarni faylga saqlash"""
    try:
        with open(USERS_FILE, "w", encoding="utf-8") as f:
            json.dump({"users": list(connected_users)}, f)
    except Exception as e:
        print(f"Error saving users: {e}")

# Bot ishga tushganda foydalanuvchilarni yuklash
load_users()


# Eng ko'p ishlatiladigan tillar ro'yxati
POPULAR_LANGUAGES = {
    "🇺🇿 O'zbek": "uz",
    "🇬🇧 Ingliz": "en",
    "🇷🇺 Rus": "ru",
    "🇹🇷 Turk": "tr",
    "🇰🇿 Qozoq": "kk",
    "🇰🇬 Qirg'iz": "ky",
    "🇹🇯 Tojik": "tg",
    "🇫🇷 Fransuz": "fr",
    "🇩🇪 Nemis": "de",
    "🇪🇸 Ispan": "es",
    "🇮🇹 Italyan": "it",
    "🇨🇳 Xitoy": "zh",
    "🇯🇵 Yapon": "ja",
    "🇰🇷 Koreys": "ko",
    "🇸🇦 Arab": "ar",
    "🇮🇳 Hindi": "hi",
    "🇵🇰 Urdu": "ur",
    "🇮🇷 Fors": "fa",
    "🔍 Avtomatik": "auto",
}


# Web App functions removed



def create_language_keyboard(prefix="from", user_id=None, show_favorites=False):
    """
    Til tanlash uchun inline keyboard yaratish
    """
    keyboard = types.InlineKeyboardMarkup(row_width=2)

    # Favorit tillarni ko'rsatish
    if show_favorites and user_id and user_id in favorite_languages:
        fav_langs = favorite_languages[user_id]
        if fav_langs:
            keyboard.add(
                types.InlineKeyboardButton(
                    "⭐ Favoritlar", callback_data=f"{prefix}_favorites"
                )
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    "📋 Barcha tillar", callback_data=f"{prefix}_all"
                )
            )
            return keyboard

    # Tugmalarni qo'shish
    buttons = []
    for lang_name, lang_code in POPULAR_LANGUAGES.items():
        callback_data = f"{prefix}_{lang_code}"
        # Favorit bo'lsa yulduzcha qo'shish
        if (
            user_id
            and user_id in favorite_languages
            and lang_code in favorite_languages[user_id]
        ):
            lang_name = f"⭐ {lang_name}"
        buttons.append(
            types.InlineKeyboardButton(lang_name, callback_data=callback_data)
        )

    # Tugmalarni 2 ta ustunda joylashtirish
    for i in range(0, len(buttons), 2):
        if i + 1 < len(buttons):
            keyboard.add(buttons[i], buttons[i + 1])
        else:
            keyboard.add(buttons[i])

    return keyboard


def save_translation_history(user_id, original, translated, from_lang, to_lang):
    """
    Tarjima tarixini saqlash
    """
    if user_id not in translation_history:
        translation_history[user_id] = []

    history_item = {
        "original": original,
        "translated": translated,
        "from_lang": from_lang,
        "to_lang": to_lang,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }

    translation_history[user_id].append(history_item)

    # Faqat oxirgi 50 ta tarjimani saqlash
    if len(translation_history[user_id]) > 50:
        translation_history[user_id] = translation_history[user_id][-50:]


@bot.message_handler(commands=["start"])
def send_welcome(message):
    """
    /start buyrug'i uchun javob funksiyasi
    """
    welcome_text = (
        "👋 Salom! Men tarjimon botman.\n\n"
        "📝 Tarjima qilish uchun:\n"
        "1️⃣ Matn yuboring yoki\n"
        "2️⃣ /translate buyrug'ini ishlating\n\n"
        "🤖 Bot: @Transalate_uz_bot\n\n"
        "💡 Siz matn yuborganingizdan keyin, tilni tanlash uchun tugmalar ko'rsatiladi.\n\n"
        "📚 Barcha buyruqlar: /help"
    )

    # Admin uchun statistika
    if is_admin(message.from_user):
        welcome_text += f"\n\n👥 Bot foydalanuvchilari: <b>{len(connected_users)}</b>"
        if not ADMIN_ID:
            welcome_text += f"\n\nℹ️ Sizning ID: <code>{message.from_user.id}</code>\n(Uni .env fayliga ADMIN_ID sifatida qo'shishingiz mumkin)"


    # Yangi foydalanuvchini saqlash
    user_id = message.from_user.id
    if user_id not in connected_users:
        connected_users.add(user_id)
        save_users()
        logging.info(f"Yangi foydalanuvchi qo'shildi: {user_id}")


    # Web App button removed
    
    keyboard = types.InlineKeyboardMarkup()
    # Web App button removed

    bot.reply_to(message, welcome_text, parse_mode="HTML", reply_markup=keyboard)


@bot.message_handler(commands=["help"])
def send_help(message):
    """
    /help buyrug'i - yordam va barcha buyruqlar
    """
    help_text = (
        "📚 **Bot buyruqlari:**\n\n"
        "/start - Botni boshlash\n"
        "/help - Yordam va barcha buyruqlar ro'yxati\n"
        "/translate - Tarjima qilish\n"
        "/multitranslate - Ko'p tilli tarjima\n"
        "/languages - Qo'llab-quvvatlanadigan tillar\n"
        "/favorites - Favorit tillar\n"
        "/history - Tarjima tarixi\n"
        "/settings - Sozlamalar\n"
        "/stats - Sizning tarjima statistikangiz\n"
        "/inline - Inline mode'ni qanday ishlatish\n\n"
        "💡 **Qanday ishlatish:**\n"
        "Matn yuboring → tillarni tanlang\n\n"
        "🔤 **Qisqa format:**\n"
        "/translate en uz Hello world\n\n"
        "📎 **Qo'shimcha:**\n"
        "• Voice message yuborish - avtomatik tarjima\n"
        "• Fayl yuborish (.txt) - fayl tarjima\n"
        "• @Transalate_uz_bot matn - inline rejimda ishlatish\n\n"
        "❓ Savollar bo'lsa, /start buyrug'ini yuboring."
    )
    bot.reply_to(message, help_text, parse_mode="HTML")


@bot.message_handler(commands=["inline"])
def inline_help_command(message):
    """
    Inline mode'ni qanday ishlatish haqida ma'lumot
    """
    inline_help_text = (
        "📲 <b>Inline Mode - Har qanday chatda foydalaning!</b>\n\n"
        "🔧 <b>Sozlash:</b>\n"
        "Inline mode allaqachon yoqilgan va ishlamoqda!\n\n"
        "📝 <b>Qanday ishlatish:</b>\n\n"
        "<b>1. Har qanday chatda yozing:</b>\n"
        "<code>@Transalate_uz_bot matn</code>\n\n"
        "<b>2. Misollar:</b>\n"
        "• <code>@Transalate_uz_bot hello world</code>\n"
        "• <code>@Transalate_uz_bot salom dunyo</code>\n"
        "• <code>@Transalate_uz_bot привет мир</code>\n"
        "• <code>@Transalate_uz_bot bonjour monde</code>\n\n"
        "<b>3. Nima bo'ladi:</b>\n"
        "✅ Bot avtomatik tilni aniqlaydi\n"
        "✅ 4 xil tilga tarjima variantlarini ko'rsatadi\n"
        "✅ Birini tanlab, chatga yuborasiz\n"
        "✅ Hammaga ko'rinadi\n\n"
        "🎯 <b>Qayerda ishlatish mumkin:</b>\n"
        "• Shaxsiy chatlarda\n"
        "• Guruhlarda\n"
        "• Kanallarda\n"
        "• Har qanday Telegram chatida!\n\n"
        "🚀 <b>Hoziroq sinab ko'ring:</b>\n"
        "Istalgan chatga o'ting va <code>@Transalate_uz_bot hello</code> yozing!"
    )

    keyboard = types.InlineKeyboardMarkup()
    # Web App button removed


    bot.reply_to(
        message, inline_help_text, parse_mode="HTML", reply_markup=keyboard
    )


@bot.message_handler(commands=["languages", "langs"])
def send_languages(message):
    """
    /languages buyrug'i - qo'llab-quvvatlanadigan tillar ro'yxati
    """
    lang_text = "🌍 <b>Qo'llab-quvvatlanadigan tillar:</b>\n\n"

    for lang_name, lang_code in POPULAR_LANGUAGES.items():
        lang_text += f"{lang_name} (<code>{lang_code}</code>)\n"

    lang_text += (
        "\n💡 <b>Eslatma:</b>\n"
        "Bot Google Translate orqali ishlaydi, shuning uchun barcha qo'llab-quvvatlanadigan tillarni qo'llab-quvvatlaydi.\n\n"
        "📝 <b>Foydalanish:</b>\n"
        "Matn yuboring va tilni tanlash tugmalaridan foydalaning."
    )

    bot.reply_to(message, lang_text, parse_mode="HTML")


@bot.message_handler(commands=["stats", "statistics"])
def send_stats(message):
    """
    /stats buyrug'i - foydalanuvchi statistikasi
    """
    user_id = message.from_user.id
    count = user_stats.get(user_id, 0)
    history_count = len(translation_history.get(user_id, []))
    fav_count = len(favorite_languages.get(user_id, []))

    stats_text = (
        f"📊 <b>Sizning statistikangiz:</b>\n\n"
        f"🔄 Jami tarjimalar: <b>{count}</b>\n"
        f"📜 Tarixda saqlangan: <b>{history_count}</b>\n"
        f"⭐ Favorit tillar: <b>{fav_count}</b>\n\n"
    )

    # Admin uchun qo'shimcha statistika
    if is_admin(message.from_user):
        stats_text += (
            f"👥 <b>Bot bo'yicha umumiy:</b>\n"
            f"👤 Jami foydalanuvchilar: <b>{len(connected_users)}</b>\n\n"
        )


    if count == 0:
        stats_text += "💡 Hali hech qanday tarjima qilmadingiz. Matn yuborib boshlang!"
    elif count < 5:
        stats_text += "🌟 Yaxshi! Davom eting!"
    elif count < 20:
        stats_text += "🔥 Ajoyib! Faol foydalanuvchisiz!"
    else:
        stats_text += "🏆 A'lo! Siz botning eng faol foydalanuvchilaridan birisisiz!"

    bot.reply_to(message, stats_text, parse_mode="HTML")


@bot.message_handler(commands=["users", "allstats"])
def all_stats_command(message):
    """
    /users buyrug'i - jami foydalanuvchilar sonini ko'rsatish (faqat admin uchun)
    """
    if not is_admin(message.from_user):
        return  # Adminga emas javob bermaslik

    total_users = len(connected_users)
    
    text = (
        f"📊 <b>Bot Statistikasi</b>\n\n"
        f"👥 Jami foydalanuvchilar: <b>{total_users}</b>\n\n"
        f"💡 Bu raqam <code>/start</code> bosgan barcha unikal foydalanuvchilarni o'z ichiga oladi."
    )
    
    bot.reply_to(message, text, parse_mode="HTML")



# Web App command removed



@bot.message_handler(commands=["multitranslate", "multi"])
def multi_translate_command(message):
    """
    Ko'p tilli tarjima - bir nechta tillarga bir vaqtda
    """
    try:
        parts = message.text.split(" ", 2)
        if len(parts) < 3:
            bot.reply_to(
                message,
                "📝 **Ko'p tilli tarjima:**\n\n"
                "Format: /multitranslate <from_lang> <matn>\n"
                "Masalan: /multitranslate en Hello world\n\n"
                "Keyin qaysi tillarga tarjima qilishni tanlang.",
            )
            return

        from_lang = parts[1].lower()
        text_to_translate = parts[2]

        if not text_to_translate.strip():
            bot.reply_to(message, "Iltimos, tarjima qilinadigan matnni kiriting.")
            return

        # Matnni saqlash
        user_id = message.from_user.id
        user_texts[user_id] = {
            "text": text_to_translate,
            "from_lang": from_lang,
            "mode": "multi",
        }

        # Ko'p tilli tarjima uchun tugmalar
        keyboard = types.InlineKeyboardMarkup(row_width=2)
        buttons = []
        for lang_name, lang_code in POPULAR_LANGUAGES.items():
            if lang_code != from_lang and lang_code != "auto":
                callback_data = f"multi_{lang_code}"
                buttons.append(
                    types.InlineKeyboardButton(lang_name, callback_data=callback_data)
                )

        # Tugmalarni qo'shish
        for i in range(0, len(buttons), 2):
            if i + 1 < len(buttons):
                keyboard.add(buttons[i], buttons[i + 1])
            else:
                keyboard.add(buttons[i])

        keyboard.add(
            types.InlineKeyboardButton(
                "✅ Barcha tillarga tarjima qilish", callback_data="multi_all"
            )
        )

        bot.reply_to(
            message,
            f"📝 Matn: {text_to_translate}\n"
            f"🔤 Manba til: {from_lang}\n\n"
            f"🌍 Qaysi tillarga tarjima qilmoqchisiz? Bir nechta tilni tanlang:",
            reply_markup=keyboard,
        )
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {str(e)}")
        logging.error(f"Multi translate error: {e}")


@bot.message_handler(commands=["favorites", "fav"])
def favorites_command(message):
    """
    Favorit tillar boshqaruvi
    """
    user_id = message.from_user.id

    if user_id not in favorite_languages:
        favorite_languages[user_id] = []

    fav_langs = favorite_languages[user_id]

    if not fav_langs:
        text = "⭐ **Favorit tillar:**\n\nHali favorit tillar qo'shilmagan.\n\nTilni favorit qilish uchun tarjima qilganda ⭐ tugmasini bosing."
    else:
        text = "⭐ **Favorit tillaringiz:**\n\n"
        for lang_code in fav_langs:
            for lang_name, code in POPULAR_LANGUAGES.items():
                if code == lang_code:
                    text += f"• {lang_name}\n"
                    break

        text += (
            "\n🗑️ Favoritdan olib tashlash uchun /favorites_remove buyrug'ini ishlating."
        )

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("➕ Favorit qo'shish", callback_data="fav_add")
    )
    if fav_langs:
        keyboard.add(
            types.InlineKeyboardButton(
                "🗑️ Favoritdan olib tashlash", callback_data="fav_remove"
            )
        )

    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(commands=["history", "hist"])
def history_command(message):
    """
    Tarjima tarixi
    """
    user_id = message.from_user.id

    if user_id not in translation_history or not translation_history[user_id]:
        bot.reply_to(
            message,
            "📜 **Tarjima tarixi:**\n\n"
            "Hali hech qanday tarjima tarixi yo'q.\n"
            "Tarjima qilganda, tarix avtomatik saqlanadi.",
        )
        return

    history = translation_history[user_id][-10:]  # Oxirgi 10 ta
    history.reverse()  # Eng yangisidan eskiroqqa

    text = "📜 **Oxirgi tarjimalar:**\n\n"

    for i, item in enumerate(history, 1):
        text += f"{i}. **{item['from_lang']}** → **{item['to_lang']}**\n"
        text += f"   📝 {item['original'][:30]}...\n"
        text += f"   🌍 {item['translated'][:30]}...\n"
        text += f"   🕐 {item['timestamp']}\n\n"

    keyboard = types.InlineKeyboardMarkup()
    keyboard.add(
        types.InlineKeyboardButton("🗑️ Tarixni tozalash", callback_data="hist_clear")
    )

    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=keyboard)


@bot.message_handler(commands=["settings", "config"])
def settings_command(message):
    """
    Sozlamalar
    """
    user_id = message.from_user.id

    if user_id not in user_settings:
        user_settings[user_id] = {
            "default_from": "auto",
            "default_to": "uz",
            "auto_save_history": True,
        }

    settings = user_settings[user_id]

    text = (
        "⚙️ **Sozlamalar:**\n\n"
        f"🔤 Default manba til: **{settings.get('default_from', 'auto')}**\n"
        f"🌍 Default maqsad til: **{settings.get('default_to', 'uz')}**\n"
        f"💾 Tarixni avtomatik saqlash: **{'Ha' if settings.get('auto_save_history', True) else "Yo'q"}**\n\n"
        "Sozlamalarni o'zgartirish uchun tugmalardan foydalaning."
    )

    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(
        types.InlineKeyboardButton(
            "🔤 Default manba", callback_data="set_default_from"
        ),
        types.InlineKeyboardButton("🌍 Default maqsad", callback_data="set_default_to"),
    )
    keyboard.add(
        types.InlineKeyboardButton(
            f"💾 Tarix: {'✅' if settings.get('auto_save_history', True) else '❌'}",
            callback_data="set_auto_history",
        )
    )

    bot.reply_to(message, text, parse_mode="Markdown", reply_markup=keyboard)


def perform_translation(text_to_translate, from_lang, to_lang):
    """
    Tarjima qilish funksiyasi
    """
    try:
        is_auto_detect = from_lang == "auto"
        detected_source = from_lang

        # Tarjima qilish (bir necha marta urinish bilan)
        max_retries = 3
        translated_text = None

        for attempt in range(max_retries):
            try:
                if is_auto_detect:
                    translator = GoogleTranslator(target=to_lang)
                else:
                    translator = GoogleTranslator(source=from_lang, target=to_lang)

                translated_text = translator.translate(text_to_translate)

                if is_auto_detect:
                    detected_source = "auto"
                else:
                    detected_source = from_lang

                break
            except Exception as retry_error:
                if attempt < max_retries - 1:
                    time.sleep(1)
                    logging.warning(
                        f"Tarjima urinishi {attempt + 1} muvaffaqiyatsiz, qayta urinilmoqda..."
                    )
                else:
                    raise retry_error

        if translated_text:
            original_text = f"📝 Asl ({detected_source}): {text_to_translate}"
            translated_result = f"🌍 Tarjima ({to_lang}): {translated_text}"
            return {
                "text": f"{original_text}\n{translated_result}",
                "original": text_to_translate,
                "translated": translated_text,
                "from_lang": detected_source,
                "to_lang": to_lang,
            }
        else:
            raise Exception("Tarjima natijasi bo'sh")
    except Exception as e:
        raise e


@bot.message_handler(commands=["translate"])
def translate_command(message):
    """
    /translate buyrug'i uchun javob funksiyasi
    Format: /translate <from_lang> <to_lang> <matn> yoki interaktiv rejim
    """
    try:
        # Xabarni bo'laklarga ajratish
        parts = message.text.split(" ", 3)

        # Agar to'liq formatda kiritilgan bo'lsa (eski usul)
        if len(parts) >= 4:
            from_lang = parts[1].lower()
            to_lang = parts[2].lower()
            text_to_translate = parts[3]

            if not text_to_translate.strip():
                bot.reply_to(message, "Iltimos, tarjima qilinadigan matnni kiriting.")
                return

            try:
                result = perform_translation(text_to_translate, from_lang, to_lang)
                response_text = result["text"] if isinstance(result, dict) else result

                # Statistika yangilash
                user_id = message.from_user.id
                user_stats[user_id] = user_stats.get(user_id, 0) + 1

                # Tarixni saqlash
                if user_id in user_settings and user_settings[user_id].get(
                    "auto_save_history", True
                ):
                    save_translation_history(
                        user_id,
                        result["original"],
                        result["translated"],
                        result["from_lang"],
                        result["to_lang"],
                    )

                # Nusxalash va qayta tarjima qilish tugmalari
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                copy_btn = types.InlineKeyboardButton(
                    "📋 Nusxalash",
                    callback_data=f"copy_{result['translated'] if isinstance(result, dict) else ''}",
                )
                retranslate_btn = types.InlineKeyboardButton(
                    "🔄 Qayta tarjima",
                    callback_data=f"retranslate_{from_lang}_{to_lang}",
                )
                keyboard.add(copy_btn, retranslate_btn)

                bot.reply_to(message, response_text, reply_markup=keyboard)
            except Exception as e:
                error_msg = (
                    f"❌ Tarjima qilishda xatolik yuz berdi.\n"
                    f"Xatolik: {str(e)}\n\n"
                    f"Iltimos, quyidagilarni tekshiring:\n"
                    f"- Internet aloqasi\n"
                    f"- Til kodlari to'g'ri kiritilganligi\n"
                    f"- Matn bo'sh emasligi"
                )
                bot.reply_to(message, error_msg)
                logging.error(f"Translation error: {e}")
        else:
            # Interaktiv rejim - matn so'rash
            bot.reply_to(
                message,
                "📝 Tarjima qilish uchun matn yuboring.\n\n"
                "Yoki quyidagi formatdan foydalaning:\n"
                "/translate <from> <to> <matn>\n"
                "Masalan: /translate en uz Hello world",
            )
    except Exception as e:
        error_message = (
            "❌ Xatolik yuz berdi. Iltimos, quyidagi formatdan foydalaning:\n"
            "/translate <from> <to> <matn>\n"
            "Masalan: /translate en uz Hello world"
        )
        bot.reply_to(message, error_message)
        logging.error(f"General error: {e}")


@bot.message_handler(content_types=["voice"])
def handle_voice(message):
    """
    Voice message'ni qayta ishlash va avtomatik tarjima
    """
    try:
        msg = bot.reply_to(message, "🎤 Ovozli xabarni qayta ishlash...")

        # Voice message'ni olish
        file_info = bot.get_file(message.voice.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Voice message'ni saqlash
        voice_file_path = os.path.join(FILES_DIR, f"voice_{message.voice.file_id}.ogg")
        with open(voice_file_path, "wb") as f:
            f.write(downloaded_file)

        # Telegram'ning voice transcription API'sidan foydalanish
        # Agar transcription mavjud bo'lsa, uni olish
        try:
            # Voice message'ni matnga o'girish uchun foydalanuvchiga so'raymiz
            # Yoki Telegram'ning transcription API'sidan foydalanish mumkin
            # Lekin hozircha oddiy yondashuv - foydalanuvchiga matn yuborishni so'raymiz

            # Voice message'ni qabul qilib, avtomatik tarjima qilish uchun so'raymiz
            keyboard = types.InlineKeyboardMarkup()
            keyboard.add(
                types.InlineKeyboardButton(
                    "🌍 Avtomatik tarjima (O'zbek)",
                    callback_data=f"voice_translate_uz_{message.voice.file_id}",
                )
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    "🌍 Avtomatik tarjima (Ingliz)",
                    callback_data=f"voice_translate_en_{message.voice.file_id}",
                )
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    "🌍 Avtomatik tarjima (Rus)",
                    callback_data=f"voice_translate_ru_{message.voice.file_id}",
                )
            )

            bot.edit_message_text(
                "🎤 **Ovozli xabar qabul qilindi!**\n\n"
                "⚠️ **Eslatma:**\n"
                "Voice message'ni to'liq tarjima qilish uchun matn kerak.\n"
                "Quyidagi variantlardan birini tanlang:\n\n"
                "1️⃣ Matn yuborib tarjima qiling\n"
                "2️⃣ Yoki quyidagi tugmalardan birini bosing (tavsiya etiladi)\n\n"
                "💡 **Maslahat:** Voice message'ni matnga o'girib, keyin yuboring.",
                message.chat.id,
                msg.message_id,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )

            # Faylni o'chirish
            try:
                os.remove(voice_file_path)
            except:
                pass

        except Exception as e:
            bot.edit_message_text(
                f"⚠️ **Eslatma:**\n\n"
                "Voice message'ni to'liq tarjima qilish uchun matn kerak.\n"
                "Iltimos, voice message'ni matnga o'girib, keyin yuboring.\n\n"
                "Yoki matn yuborib tarjima qiling.",
                message.chat.id,
                msg.message_id,
                parse_mode="Markdown",
            )
            logging.error(f"Voice message processing error: {e}")
    except Exception as e:
        bot.reply_to(message, f"❌ Xatolik: {str(e)}")
        logging.error(f"Voice message error: {e}")


@bot.message_handler(content_types=["document"])
def handle_document(message):
    """
    Fayl tarjima qilish
    """
    try:
        if not message.document:
            return

        file_name = message.document.file_name or "unknown.txt"

        # Faqat .txt fayllarni qabul qilish
        if not file_name.lower().endswith(".txt"):
            bot.reply_to(
                message,
                "⚠️ **Faqat .txt fayllar qo'llab-quvvatlanadi.**\n\n"
                "Iltimos, .txt formatidagi fayl yuboring.\n"
                "Yoki matnni nusxalab, oddiy xabar sifatida yuboring.",
                parse_mode="Markdown",
            )
            return

        msg = bot.reply_to(message, "📄 Fayl yuklanmoqda va qayta ishlanmoqda...")

        # Faylni yuklab olish
        file_info = bot.get_file(message.document.file_id)
        downloaded_file = bot.download_file(file_info.file_path)

        # Fayl mazmunini o'qish (turli encoding'larni sinab ko'rish)
        file_content = None
        encodings = ["utf-8", "utf-16", "latin-1", "cp1252"]

        for encoding in encodings:
            try:
                downloaded_file.seek(0)  # Faylni boshiga qaytarish
                file_content = downloaded_file.read().decode(encoding, errors="ignore")
                if file_content.strip():
                    break
            except:
                continue

        if not file_content or not file_content.strip():
            bot.edit_message_text(
                "❌ **Fayl bo'sh yoki o'qib bo'lmadi.**\n\n"
                "Iltimos, quyidagilarni tekshiring:\n"
                "• Fayl bo'sh emasligi\n"
                "• Fayl to'g'ri formatda ekanligi\n"
                "• Fayl UTF-8 encoding'da bo'lishi",
                message.chat.id,
                msg.message_id,
                parse_mode="Markdown",
            )
            return

        # Fayl juda katta bo'lsa, xabar berish
        if len(file_content) > 10000:
            bot.edit_message_text(
                f"⚠️ **Fayl juda katta!**\n\n"
                f"Fayl hajmi: {len(file_content)} belgi\n"
                f"Tavsiya etilgan: 10,000 belgidan kam\n\n"
                "Faylni kichik qismlarga bo'lib yuboring yoki matn sifatida yuboring.",
                message.chat.id,
                msg.message_id,
                parse_mode="Markdown",
            )
            return

        # Matnni saqlash va til tanlash
        user_id = message.from_user.id
        user_texts[user_id] = {
            "text": file_content,
            "is_file": True,
            "file_name": file_name,
        }

        keyboard = create_language_keyboard("from", user_id=user_id)
        preview_text = (
            file_content[:300] + "..." if len(file_content) > 300 else file_content
        )

        bot.edit_message_text(
            f"📄 **Fayl:** {file_name}\n"
            f"📝 **Matn:** {len(file_content)} belgi\n\n"
            f"**Ko'rinish:**\n`{preview_text}`\n\n"
            f"🔤 **Qaysi tildan tarjima qilmoqchisiz?** Manba tilni tanlang:",
            message.chat.id,
            msg.message_id,
            reply_markup=keyboard,
            parse_mode="Markdown",
        )
    except Exception as e:
        bot.reply_to(
            message,
            f"❌ **Fayl qayta ishlashda xatolik:**\n\n`{str(e)}`\n\n"
            "Iltimos, quyidagilarni tekshiring:\n"
            "• Fayl to'g'ri formatda ekanligi\n"
            "• Internet aloqasi\n"
            "• Fayl hajmi (10MB dan kichik)",
            parse_mode="Markdown",
        )
        logging.error(f"Document error: {e}")


@bot.message_handler(func=lambda message: True)
def handle_text_messages(message):
    """
    Oddiy matn xabarlarini qayta ishlash - til tanlash tugmalarini ko'rsatish
    """
    # Agar buyruq bo'lsa, e'tibor bermaslik
    if message.text.startswith("/"):
        return

    text = message.text.strip()

    # Matn bo'sh bo'lmasligini tekshirish
    if not text:
        bot.reply_to(message, "Iltimos, tarjima qilinadigan matnni kiriting.")
        return

    # Matnni saqlash
    user_id = message.from_user.id
    user_texts[user_id] = text

    # Manba tilni tanlash uchun tugmalar
    keyboard = create_language_keyboard("from", user_id=user_id)
    bot.reply_to(
        message,
        f"📝 Matn: {text}\n\n"
        "🔤 Qaysi tildan tarjima qilmoqchisiz? Manba tilni tanlang:",
        reply_markup=keyboard,
    )


@bot.inline_handler(func=lambda query: True)
def query_text(inline_query):
    """
    Inline mode - boshqa chatlarda ishlatish
    """
    try:
        query = inline_query.query.strip() if inline_query.query else ""

        logging.info(
            f"Inline query received: {query[:50]} from user {inline_query.from_user.id}"
        )

        # Agar query bo'sh bo'lsa, yordam ko'rsatish
        if not query or len(query) < 1:
            results = [
                types.InlineQueryResultArticle(
                    id="help",
                    title="📚 Tarjimon Bot - Inline Mode",
                    description="Matn yuboring va tarjima oling",
                    input_message_content=types.InputTextMessageContent(
                        message_text="📚 Tarjimon Bot - Inline Mode\n\n"
                        "Foydalanish: @Transalate_uz_bot <matn>\n\n"
                        "Masalan: @Transalate_uz_bot Hello world"
                    ),
                )
            ]
            try:
                bot.answer_inline_query(inline_query.id, results, cache_time=3600)
                logging.info("Inline query answered (help)")
            except Exception as e:
                logging.error(f"Error answering inline query (help): {e}")
            return

        if len(query) < 2:
            return

        # Matnni avtomatik tarjima qilish
        results = []

        # O'zbek tiliga tarjima
        try:
            translator_uz = GoogleTranslator(source="auto", target="uz")
            translated_uz = translator_uz.translate(query)

            if translated_uz:
                results.append(
                    types.InlineQueryResultArticle(
                        id="1",
                        title=f"🇺🇿 O'zbek: {translated_uz[:50]}",
                        description=f"Asl: {query[:50]}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"📝 Asl: {query}\n🌍 Tarjima (uz): {translated_uz}"
                        ),
                    )
                )
        except Exception as e:
            logging.error(f"UZ translation error: {e}")

        # Ingliz tiliga tarjima
        try:
            translator_en = GoogleTranslator(source="auto", target="en")
            translated_en = translator_en.translate(query)

            if translated_en:
                results.append(
                    types.InlineQueryResultArticle(
                        id="2",
                        title=f"🇬🇧 Ingliz: {translated_en[:50]}",
                        description=f"Asl: {query[:50]}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"📝 Asl: {query}\n🌍 Tarjima (en): {translated_en}"
                        ),
                    )
                )
        except Exception as e:
            logging.error(f"EN translation error: {e}")

        # Rus tiliga tarjima
        try:
            translator_ru = GoogleTranslator(source="auto", target="ru")
            translated_ru = translator_ru.translate(query)

            if translated_ru:
                results.append(
                    types.InlineQueryResultArticle(
                        id="3",
                        title=f"🇷🇺 Rus: {translated_ru[:50]}",
                        description=f"Asl: {query[:50]}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"📝 Asl: {query}\n🌍 Tarjima (ru): {translated_ru}"
                        ),
                    )
                )
        except Exception as e:
            logging.error(f"RU translation error: {e}")

        # Turk tiliga tarjima
        try:
            translator_tr = GoogleTranslator(source="auto", target="tr")
            translated_tr = translator_tr.translate(query)

            if translated_tr:
                results.append(
                    types.InlineQueryResultArticle(
                        id="4",
                        title=f"🇹🇷 Turk: {translated_tr[:50]}",
                        description=f"Asl: {query[:50]}",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"📝 Asl: {query}\n🌍 Tarjima (tr): {translated_tr}"
                        ),
                    )
                )
        except Exception as e:
            logging.error(f"TR translation error: {e}")

        # Natijalarni yuborish
        if results:
            try:
                bot.answer_inline_query(inline_query.id, results, cache_time=300)
                logging.info(
                    f"Inline query answered successfully with {len(results)} results"
                )
            except Exception as e:
                logging.error(f"Error answering inline query: {e}")
                # Xatolik bo'lsa, oddiy natija yuborish
                try:
                    error_result = [
                        types.InlineQueryResultArticle(
                            id="error",
                            title="❌ Xatolik",
                            description="Tarjima qilishda xatolik",
                            input_message_content=types.InputTextMessageContent(
                                message_text=f"❌ Xatolik: {str(e)[:100]}"
                            ),
                        )
                    ]
                    bot.answer_inline_query(inline_query.id, error_result, cache_time=1)
                except:
                    pass
        else:
            # Agar hech qanday natija bo'lmasa
            try:
                error_results = [
                    types.InlineQueryResultArticle(
                        id="error",
                        title="❌ Xatolik",
                        description="Tarjima qilishda xatolik yuz berdi",
                        input_message_content=types.InputTextMessageContent(
                            message_text=f"❌ Tarjima qilishda xatolik yuz berdi.\n\nMatn: {query}"
                        ),
                    )
                ]
                bot.answer_inline_query(inline_query.id, error_results, cache_time=1)
            except Exception as e:
                logging.error(f"Error sending error result: {e}")

    except Exception as e:
        logging.error(f"Inline handler error: {e}")
        try:
            error_results = [
                types.InlineQueryResultArticle(
                    id="error",
                    title="❌ Xatolik",
                    description="Xatolik yuz berdi",
                    input_message_content=types.InputTextMessageContent(
                        message_text="❌ Xatolik yuz berdi. Iltimos, qayta urinib ko'ring."
                    ),
                )
            ]
            bot.answer_inline_query(inline_query.id, error_results, cache_time=1)
        except Exception as e2:
            logging.error(f"Error sending error message: {e2}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("from_"))
def handle_source_language(call):
    """
    Manba til tanlanganda
    """
    try:
        from_lang = call.data.split("_")[1]
        user_id = call.from_user.id

        # Matnni olish
        if user_id not in user_texts:
            bot.answer_callback_query(
                call.id, "❌ Matn topilmadi. Iltimos, qayta matn yuboring."
            )
            return

        text = user_texts[user_id]

        # Maqsad tilni tanlash uchun tugmalar
        keyboard = create_language_keyboard("to")

        # Manba til nomini topish
        source_lang_name = "Avtomatik"
        for lang_name, lang_code in POPULAR_LANGUAGES.items():
            if lang_code == from_lang:
                # Emoji ni olib tashlash
                source_lang_name = (
                    lang_name.split(" ", 1)[-1] if " " in lang_name else lang_name
                )
                break

        bot.edit_message_text(
            f"📝 Matn: {text}\n"
            f"🔤 Manba til: {source_lang_name}\n\n"
            f"🌍 Qaysi tilga tarjima qilmoqchisiz? Maqsad tilni tanlang:",
            call.message.chat.id,
            call.message.message_id,
            reply_markup=keyboard,
        )

        # Foydalanuvchi ma'lumotlarini yangilash
        if isinstance(user_texts[user_id], str):
            user_texts[user_id] = {"text": user_texts[user_id], "from_lang": from_lang}
        else:
            user_texts[user_id] = {"text": text, "from_lang": from_lang}

        bot.answer_callback_query(call.id, f"Manba til: {source_lang_name}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Source language error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("to_"))
def handle_target_language(call):
    """
    Maqsad til tanlanganda - tarjima qilish
    """
    try:
        to_lang = call.data.split("_")[1]
        user_id = call.from_user.id

        # Foydalanuvchi ma'lumotlarini olish
        if user_id not in user_texts:
            bot.answer_callback_query(
                call.id, "❌ Matn topilmadi. Iltimos, qayta matn yuboring."
            )
            return

        user_data = user_texts[user_id]

        # Matn va manba tilni olish
        if isinstance(user_data, str):
            text = user_data
            from_lang = "auto"  # Avtomatik aniqlash
        else:
            text = user_data.get("text", "")
            from_lang = user_data.get("from_lang", "auto")

        if not text:
            bot.answer_callback_query(
                call.id, "❌ Matn topilmadi. Iltimos, qayta matn yuboring."
            )
            return

        # Tarjima qilish
        bot.answer_callback_query(call.id, "⏳ Tarjima qilinmoqda...")

        try:
            result = perform_translation(text, from_lang, to_lang)
            response_text = result["text"] if isinstance(result, dict) else result

            # Statistika yangilash
            user_stats[user_id] = user_stats.get(user_id, 0) + 1

            # Tarixni saqlash
            if user_id in user_settings and user_settings[user_id].get(
                "auto_save_history", True
            ):
                save_translation_history(
                    user_id,
                    result["original"],
                    result["translated"],
                    result["from_lang"],
                    result["to_lang"],
                )

            # Fayl tarjima bo'lsa, fayl sifatida yuborish
            user_data = user_texts.get(user_id, {})
            if isinstance(user_data, dict) and user_data.get("is_file"):
                try:
                    translated_content = result["translated"]
                    file_name = user_data.get("file_name", "translated.txt")
                    translated_file_name = f"translated_{file_name}"

                    # Faylni yozish
                    file_path = os.path.join(FILES_DIR, translated_file_name)
                    with open(file_path, "w", encoding="utf-8") as f:
                        f.write(translated_content)

                    # Faylni yuborish
                    with open(file_path, "rb") as f:
                        bot.send_document(
                            call.message.chat.id,
                            f,
                            caption=f"📄 Tarjima qilingan fayl\n🔤 {result['from_lang']} → {result['to_lang']}",
                        )

                    # Faylni o'chirish
                    os.remove(file_path)

                    bot.delete_message(call.message.chat.id, call.message.message_id)
                except Exception as e:
                    logging.error(f"File translation error: {e}")

            # Nusxalash va qayta tarjima qilish tugmalari
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            translated_text = result["translated"] if isinstance(result, dict) else ""
            copy_btn = types.InlineKeyboardButton(
                "📋 Nusxalash", callback_data=f"copy_{translated_text}"
            )
            retranslate_btn = types.InlineKeyboardButton(
                "🔄 Qayta tarjima", callback_data=f"retranslate_{from_lang}_{to_lang}"
            )
            keyboard.add(copy_btn, retranslate_btn)

            bot.edit_message_text(
                response_text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )

            # Foydalanuvchi ma'lumotlarini tozalash
            if user_id in user_texts:
                del user_texts[user_id]

        except Exception as e:
            error_msg = (
                f"❌ Tarjima qilishda xatolik yuz berdi.\n"
                f"Xatolik: {str(e)}\n\n"
                f"Iltimos, qayta urinib ko'ring."
            )
            bot.edit_message_text(
                error_msg, call.message.chat.id, call.message.message_id
            )
            logging.error(f"Translation error: {e}")

    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Target language error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("copy_"))
def handle_copy(call):
    """
    Tarjima natijasini nusxalash
    """
    try:
        translated_text = call.data.replace("copy_", "", 1)

        if translated_text:
            # Clipboard'ga nusxalash uchun foydalanuvchiga yuborish
            bot.answer_callback_query(
                call.id, f"✅ Nusxalandi: {translated_text[:50]}...", show_alert=False
            )

            # Foydalanuvchiga alohida xabar sifatida yuborish (nusxalash uchun)
            bot.send_message(
                call.message.chat.id,
                f"📋 **Nusxalash uchun:**\n\n`{translated_text}`",
                parse_mode="Markdown",
            )
        else:
            bot.answer_callback_query(call.id, "❌ Nusxalash mumkin emas")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Copy error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("retranslate_"))
def handle_retranslate(call):
    """
    Qayta tarjima qilish - teskari yo'nalishda
    """
    try:
        parts = call.data.replace("retranslate_", "").split("_")
        if len(parts) >= 2:
            old_from = parts[0]
            old_to = parts[1]

            # Teskari tarjima - eski maqsad til endi manba til bo'ladi
            new_from = old_to
            new_to = old_from

            # Xabardan matnni olish
            message_text = call.message.text
            # "Tarjima (to_lang): translated_text" formatidan matnni ajratish
            if "Tarjima" in message_text:
                lines = message_text.split("\n")
                for line in lines:
                    if "Tarjima" in line and ":" in line:
                        translated_text = line.split(":", 1)[1].strip()
                        break
                else:
                    translated_text = ""
            else:
                translated_text = ""

            if not translated_text:
                bot.answer_callback_query(call.id, "❌ Matn topilmadi")
                return

            bot.answer_callback_query(call.id, "⏳ Qayta tarjima qilinmoqda...")

            try:
                result = perform_translation(translated_text, new_from, new_to)
                response_text = result["text"] if isinstance(result, dict) else result

                # Statistika yangilash
                user_id = call.from_user.id
                user_stats[user_id] = user_stats.get(user_id, 0) + 1

                # Tugmalar
                keyboard = types.InlineKeyboardMarkup(row_width=2)
                new_translated = (
                    result["translated"] if isinstance(result, dict) else ""
                )
                copy_btn = types.InlineKeyboardButton(
                    "📋 Nusxalash", callback_data=f"copy_{new_translated}"
                )
                retranslate_btn = types.InlineKeyboardButton(
                    "🔄 Qayta tarjima", callback_data=f"retranslate_{new_from}_{new_to}"
                )
                keyboard.add(copy_btn, retranslate_btn)

                bot.edit_message_text(
                    response_text,
                    call.message.chat.id,
                    call.message.message_id,
                    reply_markup=keyboard,
                )
            except Exception as e:
                error_msg = f"❌ Qayta tarjima qilishda xatolik: {str(e)}"
                bot.edit_message_text(
                    error_msg, call.message.chat.id, call.message.message_id
                )
                logging.error(f"Retranslate error: {e}")
        else:
            bot.answer_callback_query(call.id, "❌ Xatolik: noto'g'ri format")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Retranslate error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("multi_"))
def handle_multi_translate(call):
    """
    Ko'p tilli tarjima callback handler
    """
    try:
        user_id = call.from_user.id

        if user_id not in user_texts:
            bot.answer_callback_query(call.id, "❌ Matn topilmadi")
            return

        user_data = user_texts[user_id]
        if not isinstance(user_data, dict) or user_data.get("mode") != "multi":
            bot.answer_callback_query(call.id, "❌ Noto'g'ri rejim")
            return

        text = user_data.get("text", "")
        from_lang = user_data.get("from_lang", "auto")

        if call.data == "multi_all":
            # Barcha tillarga tarjima qilish
            bot.answer_callback_query(
                call.id, "⏳ Barcha tillarga tarjima qilinmoqda..."
            )

            results = []
            target_langs = [
                code
                for name, code in POPULAR_LANGUAGES.items()
                if code != from_lang and code != "auto"
            ]

            for to_lang in target_langs[:10]:  # Faqat birinchi 10 tasi
                try:
                    result = perform_translation(text, from_lang, to_lang)
                    lang_name = next(
                        (
                            name.split(" ", 1)[-1] if " " in name else name
                            for name, code in POPULAR_LANGUAGES.items()
                            if code == to_lang
                        ),
                        to_lang,
                    )
                    results.append(
                        f"🌍 {lang_name} ({to_lang}): {result['translated']}"
                    )
                except:
                    continue

            response = f"📝 Asl ({from_lang}): {text}\n\n" + "\n".join(results)
            bot.edit_message_text(
                response, call.message.chat.id, call.message.message_id
            )
        else:
            # Bitta tilga tarjima qilish
            to_lang = call.data.replace("multi_", "")
            bot.answer_callback_query(
                call.id, f"⏳ {to_lang} tiliga tarjima qilinmoqda..."
            )

            try:
                result = perform_translation(text, from_lang, to_lang)
                response_text = result["text"]

                # Statistika yangilash
                user_stats[user_id] = user_stats.get(user_id, 0) + 1

                bot.edit_message_text(
                    response_text, call.message.chat.id, call.message.message_id
                )
            except Exception as e:
                bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Multi translate callback error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("fav_"))
def handle_favorites(call):
    """
    Favorit tillar callback handler
    """
    try:
        user_id = call.from_user.id

        if user_id not in favorite_languages:
            favorite_languages[user_id] = []

        if call.data == "fav_add":
            keyboard = create_language_keyboard("fav_add")
            bot.edit_message_text(
                "⭐ Qaysi tilni favorit qilmoqchisiz?",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )
        elif call.data == "fav_remove":
            keyboard = types.InlineKeyboardMarkup()
            for lang_code in favorite_languages[user_id]:
                lang_name = next(
                    (
                        name
                        for name, code in POPULAR_LANGUAGES.items()
                        if code == lang_code
                    ),
                    lang_code,
                )
                keyboard.add(
                    types.InlineKeyboardButton(
                        f"❌ {lang_name}", callback_data=f"fav_rm_{lang_code}"
                    )
                )

            bot.edit_message_text(
                "🗑️ Qaysi tilni favoritdan olib tashlamoqchisiz?",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )
        elif call.data.startswith("fav_add_"):
            lang_code = call.data.replace("fav_add_", "")
            if lang_code not in favorite_languages[user_id]:
                favorite_languages[user_id].append(lang_code)
                bot.answer_callback_query(call.id, f"✅ Favoritga qo'shildi")
            else:
                bot.answer_callback_query(call.id, "⚠️ Bu til allaqachon favoritda")
        elif call.data.startswith("fav_rm_"):
            lang_code = call.data.replace("fav_rm_", "")
            if lang_code in favorite_languages[user_id]:
                favorite_languages[user_id].remove(lang_code)
                bot.answer_callback_query(call.id, "✅ Favoritdan olib tashlandi")
                bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Favorites callback error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("hist_"))
def handle_history(call):
    """
    Tarix callback handler
    """
    try:
        user_id = call.from_user.id

        if call.data == "hist_clear":
            if user_id in translation_history:
                translation_history[user_id] = []
            bot.answer_callback_query(call.id, "✅ Tarix tozalandi")
            bot.delete_message(call.message.chat.id, call.message.message_id)
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"History callback error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("voice_translate_"))
def handle_voice_translate(call):
    """
    Voice message tarjima callback handler
    """
    try:
        parts = call.data.split("_")
        if len(parts) >= 4:
            target_lang = parts[2]  # uz, en, ru
            file_id = parts[3]

            bot.answer_callback_query(
                call.id,
                "⚠️ Voice message'ni to'liq tarjima qilish uchun matn kerak.\n"
                "Iltimos, voice message'ni matnga o'girib, keyin yuboring.",
            )

            # Foydalanuvchiga yordam xabari
            bot.send_message(
                call.message.chat.id,
                f"💡 **Yordam:**\n\n"
                f"Voice message'ni tarjima qilish uchun:\n"
                f"1. Voice message'ni matnga o'giring\n"
                f"2. Matnni yuboring\n"
                f"3. Manba tilni tanlang\n"
                f"4. Maqsad tilni tanlang ({target_lang})\n\n"
                f"Yoki matn yuborib, keyin {target_lang} tilini tanlang.",
                parse_mode="Markdown",
            )
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Voice translate callback error: {e}")


@bot.callback_query_handler(func=lambda call: call.data.startswith("set_"))
def handle_settings(call):
    """
    Sozlamalar callback handler
    """
    try:
        user_id = call.from_user.id

        if user_id not in user_settings:
            user_settings[user_id] = {
                "default_from": "auto",
                "default_to": "uz",
                "auto_save_history": True,
            }

        if call.data == "set_default_from":
            keyboard = create_language_keyboard("set_from")
            bot.edit_message_text(
                "🔤 Default manba tilni tanlang:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )
        elif call.data == "set_default_to":
            keyboard = create_language_keyboard("set_to")
            bot.edit_message_text(
                "🌍 Default maqsad tilni tanlang:",
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
            )
        elif call.data == "set_auto_history":
            user_settings[user_id]["auto_save_history"] = not user_settings[
                user_id
            ].get("auto_save_history", True)
            bot.answer_callback_query(
                call.id,
                f"✅ Tarix saqlash: {'Yoqildi' if user_settings[user_id]['auto_save_history'] else "O'chirildi"}",
            )

            # Sozlamalarni yangilash
            settings = user_settings[user_id]
            text = (
                "⚙️ **Sozlamalar:**\n\n"
                f"🔤 Default manba til: **{settings.get('default_from', 'auto')}**\n"
                f"🌍 Default maqsad til: **{settings.get('default_to', 'uz')}**\n"
                f"💾 Tarixni avtomatik saqlash: **{'Ha' if settings.get('auto_save_history', True) else "Yo'q"}**\n\n"
                "Sozlamalarni o'zgartirish uchun tugmalardan foydalaning."
            )
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton(
                    "🔤 Default manba", callback_data="set_default_from"
                ),
                types.InlineKeyboardButton(
                    "🌍 Default maqsad", callback_data="set_default_to"
                ),
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    f"💾 Tarix: {'✅' if settings.get('auto_save_history', True) else '❌'}",
                    callback_data="set_auto_history",
                )
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        elif call.data.startswith("set_from_"):
            lang_code = call.data.replace("set_from_", "")
            user_settings[user_id]["default_from"] = lang_code
            bot.answer_callback_query(call.id, f"✅ Default manba til: {lang_code}")

            # Sozlamalarni yangilash
            settings = user_settings[user_id]
            text = (
                "⚙️ **Sozlamalar:**\n\n"
                f"🔤 Default manba til: **{settings.get('default_from', 'auto')}**\n"
                f"🌍 Default maqsad til: **{settings.get('default_to', 'uz')}**\n"
                f"💾 Tarixni avtomatik saqlash: **{'Ha' if settings.get('auto_save_history', True) else "Yo'q"}**\n\n"
                "Sozlamalarni o'zgartirish uchun tugmalardan foydalaning."
            )
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton(
                    "🔤 Default manba", callback_data="set_default_from"
                ),
                types.InlineKeyboardButton(
                    "🌍 Default maqsad", callback_data="set_default_to"
                ),
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    f"💾 Tarix: {'✅' if settings.get('auto_save_history', True) else '❌'}",
                    callback_data="set_auto_history",
                )
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
        elif call.data.startswith("set_to_"):
            lang_code = call.data.replace("set_to_", "")
            user_settings[user_id]["default_to"] = lang_code
            bot.answer_callback_query(call.id, f"✅ Default maqsad til: {lang_code}")

            # Sozlamalarni yangilash
            settings = user_settings[user_id]
            text = (
                "⚙️ **Sozlamalar:**\n\n"
                f"🔤 Default manba til: **{settings.get('default_from', 'auto')}**\n"
                f"🌍 Default maqsad til: **{settings.get('default_to', 'uz')}**\n"
                f"💾 Tarixni avtomatik saqlash: **{'Ha' if settings.get('auto_save_history', True) else "Yo'q"}**\n\n"
                "Sozlamalarni o'zgartirish uchun tugmalardan foydalaning."
            )
            keyboard = types.InlineKeyboardMarkup(row_width=2)
            keyboard.add(
                types.InlineKeyboardButton(
                    "🔤 Default manba", callback_data="set_default_from"
                ),
                types.InlineKeyboardButton(
                    "🌍 Default maqsad", callback_data="set_default_to"
                ),
            )
            keyboard.add(
                types.InlineKeyboardButton(
                    f"💾 Tarix: {'✅' if settings.get('auto_save_history', True) else '❌'}",
                    callback_data="set_auto_history",
                )
            )
            bot.edit_message_text(
                text,
                call.message.chat.id,
                call.message.message_id,
                reply_markup=keyboard,
                parse_mode="Markdown",
            )
    except Exception as e:
        bot.answer_callback_query(call.id, f"❌ Xatolik: {str(e)}")
        logging.error(f"Settings callback error: {e}")


@bot.message_handler(content_types=["web_app_data"])
def handle_web_app_data(message):
    """
    Web App'dan kelgan ma'lumotlarni qayta ishlash
    """
    try:
        web_app_data = json.loads(message.web_app_data.data)
        user_id = message.from_user.id
        action = web_app_data.get("action")

        if action == "translation_completed":
            # Web App'dan tarjima yakunlandi
            original = web_app_data.get("original", "")
            translated = web_app_data.get("translated", "")
            from_lang = web_app_data.get("from_lang", "auto")
            to_lang = web_app_data.get("to_lang", "uz")

            # Statistika yangilash
            user_stats[user_id] = user_stats.get(user_id, 0) + 1

            # Tarixni saqlash
            if user_id in user_settings and user_settings[user_id].get(
                "auto_save_history", True
            ):
                save_translation_history(
                    user_id, original, translated, from_lang, to_lang
                )

            bot.reply_to(
                message,
                f"✅ **Web App'da tarjima bajarildi!**\n\n"
                f"📝 Asl ({from_lang}): {original}\n"
                f"🌍 Tarjima ({to_lang}): {translated}",
                parse_mode="Markdown",
            )

        elif action == "share_translation":
            # Web App'dan ulashish so'rovi
            share_text = web_app_data.get("share_text", "")
            if share_text:
                bot.send_message(user_id, share_text, parse_mode="Markdown")

    except Exception as e:
        logging.error(f"Web App data handler error: {e}")
        bot.reply_to(
            message, "❌ Web App ma'lumotlarini qayta ishlashda xatolik yuz berdi."
        )


def signal_handler(sig, frame):
    """
    Signal handler - botni to'g'ri to'xtatish
    """
    print("\n\n🛑 Bot to'xtatilmoqda...")
    try:
        bot.stop_polling()
    except:
        pass
    print("✅ Bot to'xtatildi.")
    sys.exit(0)


if __name__ == "__main__":
    """
    Web App va Botni birga ishga tushirish
    """
    # Signal handlerlarni sozlash
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    print("=" * 60)
    print("=" * 60)
    print("🚀 TARJIMON BOT ISHGA TUSHIRILMOQDA")
    print("=" * 60)
    print("📱 Telegram Bot: @Transalate_uz_bot")
    print("=" * 60)
    print("Botni to'xtatish uchun Ctrl+C bosing.")
    print("=" * 60)

    # Web App logika o'chirib tashlandi

    # Avval barcha pending updatelarni tozalash
    try:
        bot.delete_webhook()
        print("✅ Webhook tozalandi.")
        time.sleep(1)
    except Exception as e:
        logging.warning(f"Webhook tozalashda xatolik (ehtimol webhook yo'q): {e}")

    max_retries = 3
    retry_count = 0

    while retry_count < max_retries:
        try:
            # Botni polling rejimida ishga tushirish
            if retry_count > 0:
                print(
                    f"\n🔄 Botni ishga tushirishga urinish {retry_count + 1}/{max_retries}..."
                )
            else:
                print("📱 Telegram Bot ishga tushirilmoqda...")

            bot.polling(none_stop=True, interval=0, timeout=20, long_polling_timeout=20)
            break
        except KeyboardInterrupt:
            print("\n✅ Bot va Web App to'xtatildi.")
            logging.info("Bot foydalanuvchi tomonidan to'xtatildi.")
            break
        except Exception as e:
            error_msg = str(e)
            logging.error(f"Bot xatosi: {e}")

            # 409 xatolik - boshqa instance ishlamoqda
            if (
                "409" in error_msg
                or "Conflict" in error_msg
                or "getUpdates" in error_msg
            ):
                print("\n" + "=" * 50)
                print("⚠️  XATOLIK: Boshqa bot instance ishlamoqda!")
                print("=" * 50)
                print("\n📋 Iltimos, quyidagilarni bajaring:")
                print("1. Barcha bot instancelarni to'xtating (Ctrl+C)")
                print("2. Bir necha soniya kutib turing (5-10 soniya)")
                print("3. Botni qayta ishga tushiring")
                print(
                    "\n💡 Eslatma: Bir vaqtning o'zida faqat bitta bot instance ishlashi kerak!"
                )

                if retry_count < max_retries - 1:
                    wait_time = 5
                    print(f"\n⏳ {wait_time} soniya kutib, qayta urinilmoqda...")
                    time.sleep(wait_time)
                    retry_count += 1
                else:
                    print("\n❌ Maksimal urinishlar soniga yetildi.")
                    print(
                        "Iltimos, barcha bot instancelarni to'xtating va qayta urinib ko'ring."
                    )
                    print("\n💡 Yordam:")
                    print("   - Barcha terminal oynalarini yoping")
                    print("   - Task Manager'da python.exe jarayonlarini tekshiring")
                    print("   - Bot tokenini tekshiring")
                    break
            else:
                print(f"\n❌ Tarmoq yoki API xatosi: {error_msg}")
                if retry_count < max_retries - 1:
                    wait_time = 10
                    print(f"⏳ {wait_time} soniya kutib, qayta urinilmoqda...")
                    time.sleep(wait_time)
                    retry_count += 1
                else:
                    print("❌ Maksimal urinishlar soniga yetildi.")
                    break
