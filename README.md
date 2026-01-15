# Telegram Tarjimon Bot + Web App

Bu bot foydalanuvchilarga matnlarni turli tillarga tarjima qilish imkoniyatini beradi. Bot endi chiroyli Web App bilan ham birga keladi!

## ✨ Yangi! Web App Interface

🌐 **Web App** orqali quyidagi imkoniyatlardan foydalaning:
- Chiroyli va zamonaviy interfeys
- Tez tarjima va til almashish
- Tarjima tarixi va sevimlilar
- Fayl yuklash va tarjima qilish
- Nusxalash va ulashish
- Qorong'u/Yorug' rejim
- Mobil qurilmalarga moslashgan dizayn

## 🚀 Tez Boshlash

1. **Avtomatik ishga tushirish:**
   ```bash
   python run_bot.py
   ```
   Bu skript avtomatik ravishda barcha kerakli tekshiruvlarni bajaradi va bot + web app'ni ishga tushiradi.

## 📦 Manual O'rnatish

1. **Kutubxonalarni o'rnatish:**
   ```bash
   pip install -r requirements.txt
   ```

   Yoki alohida:
   ```bash
   pip install pyTelegramBotAPI==4.14.0
   pip install deep-translator==1.11.4
   pip install Flask==2.3.3
   ```

2. **Bot tokenini olish:**
   - [@BotFather](https://t.me/BotFather) ga o'ting
   - `/newbot` buyrug'ini yuboring
   - Bot nomi va username ni kiriting
   - Olingan tokenni nusxalang

3. **Bot tokenini sozlash:**
   - `bot.py` faylini oching
   - `BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"` qatorida tokenni kiriting

## 💻 Ishlatish

### Bot + Web App'ni ishga tushirish:
```bash
python bot.py
```
Bu bot va web app'ni birga ishga tushiradi:
- Telegram Bot: @Transalate_uz_bot
- Web App: http://localhost:5000

### Web App'ga kirish:
1. **Telegram bot orqali:**
   - /start buyrug'ini yuboring
   - "🌐 Web App'da ochish" tugmasini bosing
   
2. **To'g'ridan-to'g'ri brauzer orqali:**
   - http://localhost:5000 ga o'ting

3. **Telegramda botni toping va /start buyrug'ini yuboring**

3. **Tarjima qilish:**
   ```
   /translate en uz Hello world
   /translate ru uz Привет мир
   /translate uz en Salom dunyo
   /translate auto uz Hello world  (avtomatik til aniqlash)
   ```

## Buyruqlar

### Asosiy buyruqlar:
- `/start` - Botni boshlash va Web App ochish
- `/webapp` - Web App'ni ochish
- `/help` - Barcha buyruqlar ro'yxati
- `/translate <from> <to> <matn>` - Matnni tarjima qilish
  - `from` - manba til kodi (masalan: en, uz, ru, fr)
  - `to` - maqsad til kodi
  - `matn` - tarjima qilinadigan matn
  - `auto` - avtomatik til aniqlash uchun

### Qo'shimcha funksiyalar:
- `/multitranslate <from> <matn>` - Bir nechta tillarga bir vaqtda tarjima qilish
- `/favorites` - Favorit tillarni boshqarish
- `/history` - Tarjima tarixini ko'rish
- `/settings` - Bot sozlamalari (default tillar, tarix saqlash)
- `/languages` - Qo'llab-quvvatlanadigan tillar ro'yxati
- `/stats` - Sizning tarjima statistikangiz

### Qo'shimcha imkoniyatlar:
- **Inline mode**: Boshqa chatlarda `@Transalate_uz_bot matn` formatida ishlatish
  - Inline mode'ni yoqish: @BotFather ga o'ting → `/setinline` → botingizni tanlang → inline placeholder yozing (masalan: "Matn yuboring")
- **Fayl tarjima**: `.txt` fayl yuborish - avtomatik tarjima qilinadi
  - Faqat .txt fayllar qo'llab-quvvatlanadi
  - Fayl hajmi: 10,000 belgidan kam bo'lishi tavsiya etiladi
- **Voice message**: Ovozli xabarlar qabul qilinadi
  - Voice message'ni tarjima qilish uchun matn kerak
  - Voice message'ni matnga o'girib, keyin yuboring

## Qo'llab-quvvatlanadigan tillar

Bot Google Translate orqali ishlaydi, shuning uchun barcha qo'llab-quvvatlanadigan tillarni qo'llab-quvvatlaydi.

Ba'zi umumiy til kodlari:
- `en` - Ingliz
- `uz` - O'zbek
- `ru` - Rus
- `fr` - Fransuz
- `de` - Nemis
- `es` - Ispan
- `ar` - Arab
- va boshqalar...

## Xatoliklarni hal qilish

1. **"Bot xatosi" yoki "Connection error":**
   - Internet aloqasini tekshiring
   - Bot tokenini to'g'ri kiriting
   - Botni qayta ishga tushiring

2. **"Tarjima qilishda xatolik":**
   - Til kodlarini to'g'ri kiriting
   - Matn bo'sh bo'lmasligi kerak
   - Internet aloqasini tekshiring

3. **Bot javob bermayapti:**
   - Bot ishlamoqda-yu yoki yo'qligini tekshiring
   - Terminalda xatoliklar bor-yu yo'qligini ko'ring
   - Botni qayta ishga tushiring

## Qo'shimcha funksiyalar

### Inline Mode
1. @BotFather ga o'ting
2. `/setinline` buyrug'ini yuboring
3. Botingizni tanlang
4. Inline placeholder yozing (masalan: "Matn yuboring va tarjima oling")
5. Boshqa chatlarda `@Transalate_uz_bot <matn>` formatida ishlating

### Fayl Tarjima
- `.txt` fayl yuboring
- Bot avtomatik ravishda faylni o'qiydi
- Tilni tanlang va tarjima qiling
- Tarjima qilingan fayl yuklab olinadi

### Voice Message
- Voice message yuboring
- Bot qabul qiladi va yordam ko'rsatadi
- Voice message'ni matnga o'girib, keyin tarjima qiling

## 🌐 Web App Xususiyatlari

### Interfeys:
- **Zamonaviy dizayn** - Chiroyli va intuitiv interfeys
- **Responsiv** - Telefon, planshet va kompyuterda ishlaydi
- **Telegram tema** - Telegram'ning o'z temasiga moslashadi
- **Qorong'u/Yorug' rejim** - Ko'z uchun qulay

### Funksiyalar:
- **Tez tarjima** - Bir klik bilan tarjima
- **Til almashish** - Tillarni oson almashtirish
- **Tarjima tarixi** - Barcha tarjimalar saqlanadi
- **Fayl yuklash** - .txt fayllarni yuklash va tarjima qilish
- **Nusxalash** - Natijalarni oson nusxalash
- **Ulashish** - Tarjimalarni ulashish
- **Klaviatura shortcuts** - Tez ishlash uchun

### Telegram Web App:
- Bot ichida ochiladi
- Telegram ma'lumotlari bilan integratsiya
- Native mobil tajriba
- Xavfsiz va tez

## 📱 Web App'dan foydalanish

1. **Botda Web App ochish:**
   ```
   /start → "🌐 Web App'da ochish"
   /webapp
   ```

2. **Brauzerda ochish:**
   ```
   http://localhost:5000
   ```

3. **Mobil qurilmada:**
   - Local network orqali: `http://[sizning-ip]:5000`
   - Telegram Web App orqali (tavsiya etiladi)

## 🔧 Texnik ma'lumotlar

### Arxitektura:
- **Backend:** Python + Telegram Bot API + Flask
- **Frontend:** HTML5 + CSS3 + Vanilla JavaScript
- **Telegram Integration:** Telegram Web App API

### Portlar:
- **Web App:** 5000 (Flask)
- **Bot:** Telegram API orqali

### Fayllar struktura:
```
Tarjimon bot/
├── bot.py                 # Asosiy bot kodi
├── run_bot.py            # Ishga tushirish skripti
├── requirements.txt      # Python dependencies
├── webapp/               # Web App fayllari
│   ├── index.html       # Asosiy HTML
│   └── static/
│       ├── css/style.css    # Stillar
│       └── js/app.js        # JavaScript
└── translated_files/     # Tarjima qilingan fayllar
```

## 🛠️ Ishlab chiquvchilar uchun

### Sozlash:
1. Bot tokenini `bot.py` faylida o'zgartiring
2. Web App URL'ini domeningizga moslang
3. Flask portini kerak bo'lsa o'zgartiring

### Xususiylashtirish:
- CSS orqali dizaynni o'zgartirish mumkin
- JavaScript orqali yangi funksiyalar qo'shish
- Bot buyruqlarini kengaytirish

## ⚠️ Eslatmalar

- Bot Google Translate API dan foydalanadi
- Internet aloqasi talab qilinadi
- Ba'zi mamlakatlarda Google Translate bloklangan bo'lishi mumkin
- Inline mode ishlashi uchun @BotFather orqali yoqilishi kerak
- Fayl tarjima uchun faqat .txt format qo'llab-quvvatlanadi
- Web App localhost'da ishlaganda faqat local network'dan kirish mumkin
- Production uchun HTTPS va domen kerak

