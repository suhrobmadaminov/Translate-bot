#!/usr/bin/env python3
"""
Local Web App Server for Telegram Bot Testing
Bu server local testing uchun yaratilgan - ngrok kerak emas
"""

import json
import os
import threading
import time
from pathlib import Path

from flask import Flask, jsonify, render_template_string, request, send_from_directory

# Flask app yaratish
app = Flask(__name__)

# Web App HTML (inline)
HTML_CONTENT = """
<!DOCTYPE html>
<html lang="uz">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tarjimon Bot - Test Mode</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }

        body {
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            color: #333;
        }

        .container {
            max-width: 600px;
            margin: 0 auto;
            padding: 20px;
            min-height: 100vh;
            display: flex;
            flex-direction: column;
        }

        .header {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            text-align: center;
            margin-bottom: 30px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            backdrop-filter: blur(10px);
        }

        .header h1 {
            color: #2c3e50;
            margin-bottom: 10px;
            font-size: 2rem;
        }

        .header .subtitle {
            color: #7f8c8d;
            margin-bottom: 20px;
        }

        .status {
            display: inline-block;
            background: #27ae60;
            color: white;
            padding: 8px 16px;
            border-radius: 20px;
            font-size: 0.9rem;
        }

        .translation-form {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 30px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .form-group {
            margin-bottom: 20px;
        }

        label {
            display: block;
            margin-bottom: 8px;
            font-weight: 600;
            color: #2c3e50;
        }

        select, textarea, button {
            width: 100%;
            padding: 12px;
            border: 2px solid #e1e8ed;
            border-radius: 8px;
            font-size: 16px;
            transition: all 0.3s ease;
        }

        select:focus, textarea:focus {
            outline: none;
            border-color: #667eea;
            box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
        }

        textarea {
            min-height: 120px;
            resize: vertical;
            font-family: inherit;
        }

        .language-row {
            display: grid;
            grid-template-columns: 1fr auto 1fr;
            gap: 15px;
            align-items: end;
            margin-bottom: 20px;
        }

        .swap-btn {
            width: 50px;
            height: 50px;
            border-radius: 50%;
            background: #667eea;
            color: white;
            border: none;
            cursor: pointer;
            font-size: 20px;
            transition: all 0.3s ease;
        }

        .swap-btn:hover {
            background: #5a67d8;
            transform: rotate(180deg);
        }

        .translate-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            border: none;
            padding: 15px 30px;
            border-radius: 8px;
            font-size: 18px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .translate-btn:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 25px rgba(102, 126, 234, 0.3);
        }

        .translate-btn:disabled {
            opacity: 0.6;
            cursor: not-allowed;
            transform: none;
        }

        .result {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 25px;
            margin-bottom: 20px;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
            display: none;
        }

        .result.show { display: block; }

        .result h3 {
            color: #2c3e50;
            margin-bottom: 15px;
        }

        .result-text {
            background: #f8f9fa;
            padding: 15px;
            border-radius: 8px;
            border-left: 4px solid #27ae60;
            font-size: 16px;
            line-height: 1.5;
        }

        .actions {
            margin-top: 15px;
            display: flex;
            gap: 10px;
        }

        .action-btn {
            padding: 8px 16px;
            border: 2px solid #667eea;
            background: white;
            color: #667eea;
            border-radius: 6px;
            cursor: pointer;
            transition: all 0.3s ease;
        }

        .action-btn:hover {
            background: #667eea;
            color: white;
        }

        .info-panel {
            background: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            padding: 20px;
            margin-top: auto;
            text-align: center;
            box-shadow: 0 8px 32px rgba(0,0,0,0.1);
        }

        .info-panel h4 {
            color: #2c3e50;
            margin-bottom: 10px;
        }

        .info-text {
            color: #7f8c8d;
            font-size: 14px;
            line-height: 1.4;
        }

        .loading {
            display: none;
            text-align: center;
            padding: 20px;
        }

        .spinner {
            width: 40px;
            height: 40px;
            border: 4px solid #f3f3f3;
            border-top: 4px solid #667eea;
            border-radius: 50%;
            animation: spin 1s linear infinite;
            margin: 0 auto 10px;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }

        .toast {
            position: fixed;
            top: 20px;
            right: 20px;
            background: #27ae60;
            color: white;
            padding: 12px 20px;
            border-radius: 6px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
            transform: translateX(100%);
            transition: transform 0.3s ease;
            z-index: 1000;
        }

        .toast.show {
            transform: translateX(0);
        }

        .toast.error {
            background: #e74c3c;
        }

        @media (max-width: 768px) {
            .language-row {
                grid-template-columns: 1fr;
                gap: 10px;
            }

            .swap-btn {
                width: 40px;
                height: 40px;
                font-size: 16px;
                transform: rotate(90deg);
            }

            .actions {
                flex-direction: column;
            }
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🌐 Tarjimon Bot</h1>
            <p class="subtitle">Test Mode - Local Server</p>
            <span class="status">✅ Faol</span>
        </div>

        <div class="translation-form">
            <div class="language-row">
                <div class="form-group">
                    <label for="fromLang">Qaysi tildan:</label>
                    <select id="fromLang">
                        <option value="auto">🔍 Avtomatik</option>
                        <option value="uz">🇺🇿 O'zbek</option>
                        <option value="en">🇺🇸 Ingliz</option>
                        <option value="ru">🇷🇺 Rus</option>
                        <option value="fr">🇫🇷 Fransuz</option>
                        <option value="de">🇩🇪 Nemis</option>
                        <option value="es">🇪🇸 Ispan</option>
                        <option value="tr">🇹🇷 Turk</option>
                        <option value="ar">🇸🇦 Arab</option>
                    </select>
                </div>

                <button class="swap-btn" onclick="swapLanguages()">⟷</button>

                <div class="form-group">
                    <label for="toLang">Qaysi tilga:</label>
                    <select id="toLang">
                        <option value="uz">🇺🇿 O'zbek</option>
                        <option value="en">🇺🇸 Ingliz</option>
                        <option value="ru">🇷🇺 Rus</option>
                        <option value="fr">🇫🇷 Fransuz</option>
                        <option value="de">🇩🇪 Nemis</option>
                        <option value="es">🇪🇸 Ispan</option>
                        <option value="tr">🇹🇷 Turk</option>
                        <option value="ar">🇸🇦 Arab</option>
                    </select>
                </div>
            </div>

            <div class="form-group">
                <label for="inputText">Tarjima qilinadigan matn:</label>
                <textarea id="inputText" placeholder="Bu yerga matnni yozing..."></textarea>
            </div>

            <button class="translate-btn" onclick="translateText()">
                🔄 Tarjima qilish
            </button>
        </div>

        <div class="loading" id="loading">
            <div class="spinner"></div>
            <p>Tarjima qilinmoqda...</p>
        </div>

        <div class="result" id="result">
            <h3>📝 Tarjima natijasi:</h3>
            <div class="result-text" id="resultText"></div>
            <div class="actions">
                <button class="action-btn" onclick="copyResult()">📋 Nusxalash</button>
                <button class="action-btn" onclick="clearAll()">🗑️ Tozalash</button>
            </div>
        </div>

        <div class="info-panel">
            <h4>💡 Test Mode</h4>
            <p class="info-text">
                Bu local test versiyasi. Production uchun HTTPS domen va ngrok kerak.<br>
                <strong>Server:</strong> http://localhost:5000<br>
                <strong>Bot:</strong> @Transalate_uz_bot
            </p>
        </div>
    </div>

    <div class="toast" id="toast"></div>

    <script>
        // Translation function
        async function translateText() {
            const text = document.getElementById('inputText').value.trim();
            const fromLang = document.getElementById('fromLang').value;
            const toLang = document.getElementById('toLang').value;

            if (!text) {
                showToast('Iltimos, matn kiriting!', 'error');
                return;
            }

            if (fromLang === toLang && fromLang !== 'auto') {
                showToast('Bir xil tillarni tanlash mumkin emas!', 'error');
                return;
            }

            // Show loading
            document.getElementById('loading').style.display = 'block';
            document.getElementById('result').classList.remove('show');

            try {
                const response = await fetch('/api/translate', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                    },
                    body: JSON.stringify({
                        text: text,
                        from_lang: fromLang,
                        to_lang: toLang
                    })
                });

                const data = await response.json();

                if (data.success) {
                    document.getElementById('resultText').textContent = data.translated_text;
                    document.getElementById('result').classList.add('show');
                    showToast('Tarjima muvaffaqiyatli!', 'success');
                } else {
                    throw new Error(data.error || 'Noma\'lum xatolik');
                }

            } catch (error) {
                showToast('Xatolik: ' + error.message, 'error');
            } finally {
                document.getElementById('loading').style.display = 'none';
            }
        }

        // Swap languages
        function swapLanguages() {
            const fromLang = document.getElementById('fromLang');
            const toLang = document.getElementById('toLang');

            if (fromLang.value === 'auto') {
                showToast('Avtomatik rejimda almashtirish mumkin emas!', 'error');
                return;
            }

            const temp = fromLang.value;
            fromLang.value = toLang.value;
            toLang.value = temp;
        }

        // Copy result
        async function copyResult() {
            const resultText = document.getElementById('resultText').textContent;
            if (resultText) {
                try {
                    await navigator.clipboard.writeText(resultText);
                    showToast('Nusxalandi!', 'success');
                } catch (error) {
                    showToast('Nusxalashda xatolik!', 'error');
                }
            }
        }

        // Clear all
        function clearAll() {
            document.getElementById('inputText').value = '';
            document.getElementById('result').classList.remove('show');
            showToast('Tozalandi!', 'success');
        }

        // Show toast notification
        function showToast(message, type = 'success') {
            const toast = document.getElementById('toast');
            toast.textContent = message;
            toast.className = `toast ${type}`;
            toast.classList.add('show');

            setTimeout(() => {
                toast.classList.remove('show');
            }, 3000);
        }

        // Enter key support
        document.getElementById('inputText').addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'Enter') {
                translateText();
            }
        });

        // Set default languages
        document.getElementById('fromLang').value = 'auto';
        document.getElementById('toLang').value = 'uz';
    </script>
</body>
</html>
"""


@app.route("/")
def index():
    """Asosiy sahifa"""
    return render_template_string(HTML_CONTENT)


@app.route("/api/translate", methods=["POST"])
def api_translate():
    """Tarjima API endpoint"""
    try:
        data = request.get_json()
        text = data.get("text", "").strip()
        from_lang = data.get("from_lang", "auto")
        to_lang = data.get("to_lang", "uz")

        if not text:
            return jsonify({"success": False, "error": "Matn bo'sh"})

        # Google Translator import (optional, agar mavjud bo'lsa)
        try:
            from deep_translator import GoogleTranslator

            # Tarjima qilish
            if from_lang == "auto":
                translator = GoogleTranslator(target=to_lang)
            else:
                translator = GoogleTranslator(source=from_lang, target=to_lang)

            translated_text = translator.translate(text)

            return jsonify(
                {
                    "success": True,
                    "original_text": text,
                    "translated_text": translated_text,
                    "from_lang": from_lang,
                    "to_lang": to_lang,
                }
            )

        except ImportError:
            # Mock translation agar deep_translator yo'q bo'lsa
            mock_translations = {
                "uz": f"[O'zbek] {text}",
                "en": f"[English] {text}",
                "ru": f"[Русский] {text}",
                "fr": f"[Français] {text}",
                "de": f"[Deutsch] {text}",
                "es": f"[Español] {text}",
                "tr": f"[Türkçe] {text}",
                "ar": f"[العربية] {text}",
            }

            translated_text = mock_translations.get(
                to_lang, f"[{to_lang.upper()}] {text}"
            )

            return jsonify(
                {
                    "success": True,
                    "original_text": text,
                    "translated_text": translated_text,
                    "from_lang": from_lang,
                    "to_lang": to_lang,
                    "note": "Mock translation - deep_translator not available",
                }
            )

    except Exception as e:
        return jsonify({"success": False, "error": str(e)})


@app.route("/health")
def health():
    """Server health check"""
    return jsonify({"status": "ok", "message": "Local Web App Server running"})


def get_local_ip():
    """Local IP manzilini olish"""
    try:
        import socket

        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
        return local_ip
    except:
        return "localhost"


def main():
    """Serverni ishga tushirish"""
    print("🌐 LOCAL WEB APP SERVER")
    print("=" * 40)

    local_ip = get_local_ip()

    print(f"🏠 Local: http://localhost:5000")
    print(f"📱 Network: http://{local_ip}:5000")
    print("=" * 40)
    print("💡 Bu test server - production emas!")
    print("🔧 Production uchun ngrok yoki domen kerak")
    print("🛑 To'xtatish: Ctrl+C")
    print("=" * 40)

    try:
        app.run(host="0.0.0.0", port=5000, debug=False)
    except KeyboardInterrupt:
        print("\n✅ Server to'xtatildi.")


if __name__ == "__main__":
    main()
