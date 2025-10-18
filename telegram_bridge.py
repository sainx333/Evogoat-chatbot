import requests
import time
import os

# Load your bot token from environment or paste directly (not recommended)
TOKEN = os.getenv("TELEGRAM_TOKEN", "PASTE_YOUR_TOKEN_HERE")
CHAT_URL = f"https://api.telegram.org/bot{TOKEN}"

BACKEND_URL = "https://evogoat-chatbot-eoow.onrender.com"

def send_message(chat_id, text, reply_markup=None):
    data = {"chat_id": chat_id, "text": text}
    if reply_markup:
        data["reply_markup"] = reply_markup
    requests.post(f"{CHAT_URL}/sendMessage", json=data)

def get_updates(offset=None):
    params = {"timeout": 100, "offset": offset}
    r = requests.get(f"{CHAT_URL}/getUpdates", params=params)
    return r.json()

def show_menu(chat_id):
    menu = {
        "keyboard": [
            [{"text": "💡 Learn"}, {"text": "📈 Status"}],
            [{"text": "❓ Help"}]
        ],
        "resize_keyboard": True,
        "one_time_keyboard": False
    }
    send_message(chat_id, "Evogoat is ready. Choose an action:", reply_markup=menu)

def handle_text(chat_id, text):
    text_lower = text.lower().strip()

    if text_lower == "/start":
        show_menu(chat_id)
        return

    elif "help" in text_lower:
        send_message(chat_id, "Use 💡 Learn to teach me something new.\nUse 📈 Status to check my state.")
        return

    elif "status" in text_lower:
        try:
            r = requests.get(f"{BACKEND_URL}/health")
            if r.status_code == 200:
                send_message(chat_id, "✅ Evogoat backend is online.")
            else:
                send_message(chat_id, "⚠️ Backend might be offline.")
        except Exception as e:
            send_message(chat_id, f"❌ Error checking status: {e}")
        return

    elif "learn" in text_lower or text_lower.startswith("/learn"):
        send_message(chat_id, "What should I learn from?")
        return "awaiting_input"

    else:
        # Default: treat input as a learning snippet
        try:
            r = requests.post(f"{BACKEND_URL}/learn", json={"content": text})
            data = r.json()
            if "error" in data:
                send_message(chat_id, f"⚠️ Error: {data['error']}")
            else:
                fitness = data["result"]["fitness"]
                send_message(chat_id, f"🧠 Learned from your input.\nFitness: {fitness:.3f}")
        except Exception as e:
            send_message(chat_id, f"⚙️ Error contacting backend: {e}")
        return

def run():
    print("🤖 Evogoat Telegram bridge with menu active.")
    offset = None
    user_states = {}

    while True:
        updates = get_updates(offset)
        if "result" in updates:
            for update in updates["result"]:
                offset = update["update_id"] + 1
                message = update.get("message")
                if not message:
                    continue
                chat_id = message["chat"]["id"]
                text = message.get("text", "")

                state = user_states.get(chat_id, None)
                if state == "awaiting_input":
                    user_states[chat_id] = None
                    handle_text(chat_id, text)
                else:
                    new_state = handle_text(chat_id, text)
                    if new_state:
                        user_states[chat_id] = new_state
        time.sleep(1)

if __name__ == "__main__":
    run()
