import json
import time
import numpy as np
import zstandard as zstd
from hashlib import sha3_512
from pathlib import Path


STATE_FILE = Path("data/state.json")


class EvoCore:
    """
    A lightweight evolutionary core that mutates a simple numeric model
    and persists its state to disk between learning calls.
    """

    def __init__(self, model=None):
        # Create a simple default model if none provided
        if model is None:
            self.model = type("SimpleModel", (), {
                "weights": np.random.randn(4),
                "fitness": 0.0,
                "mutate": lambda self, rng: self,
                "serialize": lambda self: self.weights.tolist()
            })()
        else:
            self.model = model

        # Load previous state if exists
        if STATE_FILE.exists():
            try:
                data = json.loads(STATE_FILE.read_text())
                self.model.weights = np.array(data.get("weights", self.model.weights))
                self.model.fitness = data.get("fitness", 0.0)
            except Exception:
                pass

    def evolve(self, snippet: str, fitness_func):
        """
        Mutate the model deterministically based on the snippet
        and compute new fitness. Save compressed state afterward.
        """
        seed = int(sha3_512(snippet.encode()).hexdigest()[:16], 16)
        rng = np.random.default_rng(seed)

        # Generate new candidate
        new_weights = self.model.weights + rng.normal(0, 0.1, size=self.model.weights.shape)
        new_fitness = fitness_func(new_weights)

        if new_fitness > self.model.fitness:
            self.model.weights = new_weights
            self.model.fitness = new_fitness

        # Compress + store state
        state_data = json.dumps({
            "weights": self.model.weights.tolist(),
            "fitness": self.model.fitness,
            "timestamp": time.time()
        }).encode()

        compressed = zstd.ZstdCompressor(level=5).compress(state_data)
        STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        STATE_FILE.write_bytes(compressed)

        return sha3_512(state_data).hexdigest(), self.model.fitness
