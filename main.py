from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
import json, os, random

app = FastAPI(title="Evogoat Chatbot")

DATA_FILE = "data/chat_history.json"

if not os.path.exists("data"):
    os.makedirs("data")

# tiny memory
def load_history():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return json.load(f)
    return []

def save_history(history):
    with open(DATA_FILE, "w") as f:
        json.dump(history, f)

history = load_history()

@app.get("/", response_class=HTMLResponse)
def chat_ui():
    html = """
    <html><body style="font-family:sans-serif;max-width:600px;margin:auto;">
      <h2>Evogoat Chatbot</h2>
      <div id="chatbox" style="border:1px solid #ccc;padding:10px;height:300px;overflow:auto;"></div>
      <form id="chatForm" onsubmit="sendMessage();return false;">
        <input id="userInput" placeholder="Type a message..." style="width:80%%;">
        <input type="submit" value="Send">
      </form>
      <script>
        async function sendMessage(){
          const text = document.getElementById('userInput').value;
          document.getElementById('userInput').value='';
          const res = await fetch('/chat', {
            method:'POST',
            headers:{'Content-Type':'application/json'},
            body:JSON.stringify({message:text})
          });
          const data = await res.json();
          const box=document.getElementById('chatbox');
          box.innerHTML += '<b>You:</b> '+text+'<br><b>Evogoat:</b> '+data.reply+'<br><br>';
          box.scrollTop = box.scrollHeight;
        }
      </script>
    </body></html>
    """
    return html

@app.post("/chat")
async def chat(request: Request):
    data = await request.json()
    message = data.get("message", "").strip()
    if not message:
        return JSONResponse({"reply": "Say something first."})
    # simple pseudo-response logic
    response_options = [
        "Interesting...",
        "Tell me more about that.",
        "Why do you think that?",
        "Hmm, I hadn't considered that.",
        "Let's explore that idea further."
    ]
    reply = random.choice(response_options)
    history.append({"user": message, "bot": reply})
    save_history(history)
    return JSONResponse({"reply": reply})
