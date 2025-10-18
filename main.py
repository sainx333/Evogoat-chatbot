from pydantic import BaseModel
from fastapi import FastAPI
from agent.evo_core import EvoCore
import numpy as np

app = FastAPI(title="Evogoat AI")

# --- Simple base model class ---
class SimpleModel:
    def __init__(self):
        self.weights = np.random.randn(4)
        self.fitness = 0.0

    def predict(self, inputs):
        return float(np.dot(self.weights, inputs))

    def mutate(self, rng):
        child = SimpleModel()
        child.weights = self.weights + rng.normal(0, 0.1, size=self.weights.shape)
        return child

    def serialize(self):
        return self.weights.tolist()

# Initialize EvoCore (no argument, since EvoCore builds its own model)
core = EvoCore()

# --- Request model for /learn ---
class LearnRequest(BaseModel):
    content: str

@app.get("/health")
def health():
    return {"ok": True}

@app.post("/learn")
def learn(request: LearnRequest):
    snippet = request.content
    hash_value, fitness = core.evolve(snippet, lambda m: np.random.rand())
    return {"message": "Evolution step complete",
            "result": {"fitness": fitness, "snippet": snippet}}
