from fastapi import FastAPI
from pydantic import BaseModel
from agent.evo_core import EvoCore
import numpy as np

# --- Simple model class the AI evolves ---
class SimpleModel:
    def __init__(self):
        self.weights = np.random.randn(4)
        self.fitness = 0.0

    def predict(self, inputs):
        return float(np.dot(self.weights, inputs))

    def mutate(self):
        self.weights += np.random.normal(0, 0.1, size=self.weights.shape)

# --- Initialize FastAPI and the core engine ---
app = FastAPI(title="Evogoat AI")

core = EvoCore()  # uses default model internally if coded that way

# --- Data model for incoming POST requests ---
class LearnRequest(BaseModel):
    content: str

# --- Health check ---
@app.get("/health")
def health():
    return {"ok": True}

# --- Root route (nice welcome message) ---
@app.get("/")
def home():
    return {"message": "Evogoat AI is alive and evolving!"}

# --- Learning endpoint ---
@app.post("/learn")
def learn(request: LearnRequest):
    snippet = request.content
    # call your evolution logic from evo_core
    hash_value, fitness = core.evolve(snippet)
    return {
        "message": "Evolution step complete",
        "result": {"hash": hash_value, "fitness": fitness, "snippet": snippet},
    }
