import os
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

COBALT_API = "https://api.cobalt.tools/api/json"

# Asosiy menyuni yaratish
def main_menu():
    keyboard = [
        ["📤 Video yuklash"]
    ]
    return Reply_keyboard_markup(keyboard, resize_keyboard=True, one_time_keyboard=False)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Assalomu alaykum! 📥 Ishtimoiy tarmoq havolasini yuboring (TikTok, Instagram, YouTube, X, Facebook, Reddit).",
        reply_markup=main_menu()
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    chat_id = update.effective_chat.id

    # "Orqaga" yoki "Video yuklash" tugmasi bosilsa
    if text in ["📤 Video yuklash", "🔙 Orqaga"]:
        await start(update, context)
        return

    # URL tekshirish
    supported = ["tiktok.com", "instagram.com", "youtube.com", "youtu.be", "twitter.com", "x.com", "facebook.com", "reddit.com"]
    if not any(domain in text for domain in supported):
        await update.message.reply_text(
            "⚠️ Faqat quyidagi tarmoqlardan havola yuboring:\n"
            "TikTok, Instagram, YouTube, X (Twitter), Facebook, Reddit."
        )
        return

    await update.message.reply_text("⏳ Yuklanmoqda... Iltimos, kuting.")

    try:
        # Cobalt API so'rovi
        resp = requests.post(
            COBALT_API,
            json={"url": text},
            headers={"Accept": "application/json"},
            timeout=30
        )
        resp.raise_for_status()
        data = resp.json()

        if data.get("status") == "error":
            await update.message.reply_text(f"❌ Xatolik: {data.get('text', 'Nomaʼlum xato')}")
            return

        dl_url = data.get("url")
        if not dl_url:
            await update.message.reply_text("📥 Yuklab olish uchun havola topilmadi.")
            return

        # Javob turiga qarab yuborish
        media_type = data.get("type", "unknown")
        if media_type == "video":
            await update.message.reply_video(video=dl_url, supports_streaming=True)
        elif media_type == "photo":
            await update.message.reply_photo(photo=dl_url)
        elif media_type == "audio":
            await update.message.reply_audio(audio=dl_url)
        else:
            await update.message.reply_document(document=dl_url)

    except requests.exceptions.Timeout:
        await update.message.reply_text("⏱️ So'rov vaqti tugadi. Iltimos, qaytadan urinib ko'ring.")
    except Exception as e:
        await update.message.reply_text(f"❌ Xatolik: {str(e)}")

# Asosiy botni ishga tushirish
if __name__ == "__main__":
    TOKEN = os.getenv("BOT_TOKEN")
    if not TOKEN:
        raise ValueError("BOT_TOKEN muhit o'zgaruvchisi sozlanmagan!")

    app = Application.builder().token(TOKEN).build()
    app.add_handler(MessageHandler(filters.Regex("^/start$"), start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()
