#!/usr/bin/env python3
import os, requests, asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# Read your token from environment
TOKEN = os.getenv("TELEGRAM_TOKEN")
API_URL = os.getenv("EVO_API", "https://evogoat-chatbot-eoow.onrender.com")

if not TOKEN:
    raise ValueError("Missing TELEGRAM_TOKEN environment variable")

menu = [["💡 Learn", "📈 Status"], ["❓ Help"]]

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Evogoat is ready. Choose an action:",
        reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True)
    )

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "💬 Send me text to evolve Evogoat’s brain.\n"
        "Use /status to check if it’s healthy."
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        r = requests.get(f"{API_URL}/health")
        if r.ok:
            await update.message.reply_text("✅ Evogoat is healthy.")
        else:
            await update.message.reply_text("⚠️ Evogoat seems offline.")
    except Exception as e:
        await update.message.reply_text(f"Error contacting API: {e}")

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    snippet = update.message.text.strip()
    try:
        data = {"content": snippet}
        r = requests.post(f"{API_URL}/learn", json=data)
        resp = r.json()
        if "error" in resp:
            await update.message.reply_text(f"⚠️ {resp['error']}")
        else:
            fit = resp['result'].get('fitness', '?')
            await update.message.reply_text(f"✅ Learned snippet. Fitness: {fit:.4f}")
    except Exception as e:
        await update.message.reply_text(f"Request failed: {e}")

async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text.startswith("💡") or text.startswith("📈") or text.startswith("❓"):
        # Ignore the button icons and route to commands
        if "Learn" in text:
            await update.message.reply_text("Send a message for Evogoat to learn from:")
        elif "Status" in text:
            await status(update, context)
        elif "Help" in text:
            await help_cmd(update, context)
    else:
        await learn(update, context)

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("status", status))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))
    print("Evogoat Telegram bridge active.")
    app.run_polling()

if __name__ == "__main__":
    main()
