# Simple self-evolving learning core for Evogoat.
# Pure Python + math; runs fast even on a phone.

import json, random, math
from pathlib import Path

STATE_FILE = Path("data/state.json")

class EvoCore:
    def __init__(self, n=4, lr=0.1):
        self.n = n
        self.lr = lr
        self.weights = [random.uniform(-1, 1) for _ in range(n)]
        self.load()

    def load(self):
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text())
                self.weights = data["weights"]
            except Exception:
                pass

    def save(self):
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_text(json.dumps({"weights": self.weights}))

    def act(self, inputs):
        """Produce an output from numeric inputs."""
        return math.tanh(sum(w * x for w, x in zip(self.weights, inputs)))

    def evolve(self, inputs, target):
        """Adjust weights toward target outcome."""
        out = self.act(inputs)
        error = target - out
        for i in range(self.n):
            self.weights[i] += self.lr * error * inputs[i]
        return error
