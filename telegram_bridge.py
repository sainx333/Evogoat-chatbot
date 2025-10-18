import os
import requests
from telegram import Update, KeyboardButton, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

API_URL = os.getenv("EVO_API_URL", "https://evogoat-chatbot-eoow.onrender.com")

# --- Commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[KeyboardButton("💡 Learn"), KeyboardButton("📊 Status")]]
    await update.message.reply_text(
        "🐐 Welcome to Evogoat! Choose an option:",
        reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    )

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip().lower()

    if text in ("💡 learn", "learn"):
        await update.message.reply_text("Send me something new to learn!")
    elif text in ("📊 status", "status"):
        try:
            res = requests.get(f"{API_URL}/health", timeout=10)
            data = res.json()
            await update.message.reply_text(f"✅ Status: {data}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Couldn't reach Evogoat: {e}")
    else:
        try:
            res = requests.post(f"{API_URL}/learn", json={"content": text}, timeout=15)
            data = res.json()
            if "message" in data:
                await update.message.reply_text(f"🤖 {data['message']}")
            else:
                await update.message.reply_text(f"⚠️ Error: {data}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Failed to connect: {e}")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Commands:\n"
        "/start - show menu\n"
        "/help - show this message\n"
        "Send any text to let Evogoat learn!"
    )

# --- Main bot setup ---
def main():
    if not BOT_TOKEN:
        print("❌ TELEGRAM_TOKEN not found in environment!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🐐 Evogoat Telegram bridge active.")
    app.run_polling()

if __name__ == "__main__":
    main()
