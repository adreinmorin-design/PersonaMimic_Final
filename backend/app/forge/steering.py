"""
app/forge/steering.py - Industrial Activation Steering
Based on 2025 SAS (Sparse Activation Steering) standards.
Allows PersonaMimic to nudge model behavior at the activation layer.
"""

import logging
from typing import Any, Callable

import torch

logger = logging.getLogger("forge.steering")


class SteeringVector:
    """Represents a pre-computed or real-time steering vector for a specific feature."""

    def __init__(self, name: str, layer: int, vector: torch.Tensor, coefficient: float = 1.0):
        self.name = name
        self.layer = layer
        self.vector = vector
        self.coefficient = coefficient


class ActivationSteerer:
    """Manages the injection of steering vectors into the model's forward pass."""

    def __init__(self):
        self.active_vectors: list[SteeringVector] = []
        self._hooks = []

    def add_vector(self, name: str, layer: int, vector_data: list[float], coefficient: float = 1.0):
        """Register a new steering vector (from pre-computed SAELens features)."""
        vector = torch.tensor(vector_data)
        self.active_vectors.append(SteeringVector(name, layer, vector, coefficient))
        logger.info(f"Steering Feature Loaded: {name} (Layer {layer}, Coeff {coefficient})")

    def wrap_model(self, model: Any):
        """
        Applies hooks to a PyTorch-based model (compatible with TransformerLens/SAELens).
        Note: Local Ollama uses a closed binary for inference, but our 'Model Forge'
        uses TransformerLens for white-box steering sessions.
        """
        if not hasattr(model, "add_hook"):
            logger.warning("Model does not support standard hooks. Steering skipped.")
            return model

        for vec in self.active_vectors:
            hook_fn = self._make_steering_hook(vec)
            hook = model.add_hook(f"blocks.{vec.layer}.hook_resid_post", hook_fn)
            self._hooks.append(hook)

        return model

    def _make_steering_hook(self, vector_obj: SteeringVector) -> Callable:
        def steering_hook(resid_post: torch.Tensor, hook: Any):
            # Apply the steering vector to the residual stream
            # res_post: (batch, seq, d_model)
            return resid_post + (vector_obj.vector * vector_obj.coefficient)

        return steering_hook

    def clear(self):
        """Remove all active steering vectors."""
        self.active_vectors = []
        for hook in self._hooks:
            # Assuming TransformerLens standard
            if hasattr(hook, "remove"):
                hook.remove()
        self._hooks = []


# Singleton instance for the forge
steer_service = ActivationSteerer()

# PRE-COMPUTED INDUSTRIAL FEATURES (Placeholder representations for Llama-3.1-8B)
# In production, these are loaded from SAELens JSON exports.
INDUSTRIAL_STEERING_COLLECTION = {
    "code_completeness": {
        "layer": 12,
        "vector": [0.01] * 4096,  # Simplified d_model representation
        "description": "Suppresses 'pass' and 'TODO' by steering toward functional implementation features.",
    },
    "brand_alignment": {
        "layer": 8,
        "vector": [0.005] * 4096,
        "description": "Nudges model to prioritize Dre-branded headers and industrial tone.",
    },
}
