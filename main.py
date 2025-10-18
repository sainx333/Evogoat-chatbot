from fastapi import FastAPI
from pydantic import BaseModel
from agent.evo_core import EvoCore
import numpy as np

# --- Core setup ---
app = FastAPI(title="Evogoat AI")

# Initialize global EvoCore (persistent across requests)
core = EvoCore()

# --- Simple request model ---
class LearnRequest(BaseModel):
    content: str

# --- Root welcome route ---
@app.get("/")
def home():
    return {"message": "Evogoat AI is alive and evolving!"}

# --- Health check route ---
@app.get("/health")
def health():
    return {"ok": True}

# --- Learning route with error handling ---
@app.post("/learn")
def learn(request: LearnRequest):
    snippet = request.content
    try:
        hash_value, fitness = core.evolve(snippet)
        return {
            "message": "Evolution step complete",
            "result": {
                "hash": hash_value,
                "fitness": fitness,
                "snippet": snippet
            }
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"error": str(e), "snippet": snippet}

# --- Optional status route for monitoring ---
@app.get("/status")
def status():
    try:
        state = core.get_state() if hasattr(core, "get_state") else {}
        return {"status": "running", "state": state}
    except Exception as e:
        return {"status": "error", "error": str(e)}
