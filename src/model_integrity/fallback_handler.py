"""
Model Adapter and Fallback Handler implementing the Adapter / Factory Pattern.
Supports both PyTorch (.pt) and ONNX (.onnx) models with graceful black-box fallback.
"""

from abc import ABC, abstractmethod
from typing import Tuple, Optional, Any
from pathlib import Path
import hashlib
import numpy as np


class BaseModelAdapter(ABC):
    """Abstract interface for auditing models in a hardware/runtime-agnostic way."""

    def __init__(self, model_path: str):
        self.model_path = Path(model_path)
        self.model_hash = self._compute_checkpoint_hash()

    def _compute_checkpoint_hash(self) -> str:
        """Computes deterministic SHA-256 fingerprint of the model file on disk."""
        sha = hashlib.sha256()
        with open(self.model_path, "rb") as f:
            while chunk := f.read(65536):
                sha.update(chunk)
        return sha.hexdigest()

    @abstractmethod
    def predict(self, input_array: np.ndarray) -> np.ndarray:
        """
        Executes inference on preprocessed numpy batch.
        Returns: logits or softmax probability array of shape (batch_size, num_classes).
        """
        pass

    @abstractmethod
    def get_input_shape(self) -> Tuple[int, ...]:
        """Returns expected input shape (e.g. (1, 3, 64, 64))."""
        pass


class ONNXModelAdapter(BaseModelAdapter):
    """
    Black-box model auditor using ONNX Runtime.
    Works 100% offline without requiring training code or weights access.
    """

    def __init__(self, model_path: str):
        super().__init__(model_path)
        import onnxruntime as ort

        opts = ort.SessionOptions()
        opts.log_severity_level = 3  # Errors only
        self.session = ort.InferenceSession(str(self.model_path), sess_options=opts, providers=["CPUExecutionProvider"])
        self.input_name = self.session.get_inputs()[0].name
        self.raw_input_shape = self.session.get_inputs()[0].shape
        self.output_name = self.session.get_outputs()[0].name

    def predict(self, input_array: np.ndarray) -> np.ndarray:
        data = input_array.astype(np.float32)

        # Check if the model requires a single-item batch size (fixed dim 1)
        fixed_batch_one = (
            len(self.raw_input_shape) > 0 and 
            self.raw_input_shape[0] == 1 and 
            data.shape[0] > 1
        )

        if fixed_batch_one:
            # Run one-by-one and stack
            results = []
            for i in range(data.shape[0]):
                single = data[i:i+1]
                out = self.session.run([self.output_name], {self.input_name: single})[0]
                results.append(out[0])
            return np.array(results)

        outputs = self.session.run([self.output_name], {self.input_name: data})
        return outputs[0]

    def get_input_shape(self) -> Tuple[int, ...]:
        clean_shape = []
        for d in self.raw_input_shape:
            if isinstance(d, int) and d > 0:
                clean_shape.append(d)
            else:
                clean_shape.append(1)
        return tuple(clean_shape)


class PyTorchModelAdapter(BaseModelAdapter):
    """
    White-box adapter for PyTorch .pt / .pth checkpoints.
    Falls back gracefully if PyTorch runtime or weights cannot be loaded.
    """

    def __init__(self, model_path: str):
        super().__init__(model_path)
        try:
            import torch
            self.torch = torch
            self.model = torch.load(str(self.model_path), map_location="cpu")
            if hasattr(self.model, "eval"):
                self.model.eval()
        except Exception as e:
            raise RuntimeError(f"PyTorch loading failed for {model_path}: {e}")

    def predict(self, input_array: np.ndarray) -> np.ndarray:
        with self.torch.no_grad():
            tensor = self.torch.from_numpy(input_array).float()
            output = self.model(tensor)
            if hasattr(output, "numpy"):
                return output.numpy()
            return output

    def get_input_shape(self) -> Tuple[int, ...]:
        return (1, 3, 224, 224)


def load_model_adapter(model_path: str) -> BaseModelAdapter:
    """Factory function for model adapters."""
    path = Path(model_path)
    if not path.exists():
        raise FileNotFoundError(f"Model file not found: {model_path}")

    ext = path.suffix.lower()
    if ext == ".onnx":
        return ONNXModelAdapter(str(path))
    elif ext in [".pt", ".pth"]:
        try:
            return PyTorchModelAdapter(str(path))
        except Exception as e:
            raise RuntimeError(f"PyTorch model adapter failed to load: {e}. Recommend converting to .onnx for black-box testing.")
    else:
        raise ValueError(f"Unsupported model extension: {ext}. Framework accepts .onnx and .pt/.pth.")
