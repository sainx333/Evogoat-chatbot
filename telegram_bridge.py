import os
import asyncio
import logging
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = os.getenv("TELEGRAM_TOKEN")

if not BOT_TOKEN:
    raise SystemExit("❌ TELEGRAM_TOKEN not found in environment!")

BACKEND_URL = os.getenv("BACKEND_URL", "https://evogoat-chatbot-zoks.onrender.com")

# --- Basic commands ---

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["/menu", "/learn"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Welcome to Evogoat! Choose an option below or type a message to evolve.",
        reply_markup=reply_markup
    )

async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "🧠 *Evogoat Menu*\n\n"
        "/learn — Teach Evogoat something new\n"
        "/health — Check system status\n"
        "/about — Learn about this project"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def about(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Evogoat is an adaptive AI experiment built with FastAPI and Telegram.")

# --- Interaction with FastAPI backend ---

async def learn(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Send a short message to teach Evogoat.")
    context.user_data["awaiting_learning"] = True

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if context.user_data.get("awaiting_learning"):
        snippet = update.message.text
        context.user_data["awaiting_learning"] = False

        try:
            response = requests.post(f"{BACKEND_URL}/learn", json={"content": snippet})
            data = response.json()
            await update.message.reply_text(f"✅ Learned: {data}")
        except Exception as e:
            await update.message.reply_text(f"⚠️ Error communicating with backend: {e}")
    else:
        await update.message.reply_text("Use /menu to see available commands.")

# --- App entry point ---

async def main():
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .concurrent_updates(True)
        .build()
    )

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("menu", menu))
    app.add_handler(CommandHandler("about", about))
