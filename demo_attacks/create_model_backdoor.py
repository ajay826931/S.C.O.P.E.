"""
Demo Script: Generate Clean and Backdoored Models (ONNX format).
Constructs a valid computer vision classifier model and an infected Trojan model
for security auditing and validation.
"""

import sys
import types
from pathlib import Path
import numpy as np

if "ml_dtypes" not in sys.modules:
    class _MockModule(types.ModuleType):
        def __getattr__(self, name):
            return np.float32
    _mock_ml = _MockModule("ml_dtypes")
    _mock_ml._ml_dtypes_ext = _MockModule("_ml_dtypes_ext")
    sys.modules["ml_dtypes"] = _mock_ml
    sys.modules["ml_dtypes._ml_dtypes_ext"] = _mock_ml._ml_dtypes_ext

import onnx
from onnx import helper, TensorProto


def create_classifier_model(output_path: str, is_backdoored: bool = False, num_classes: int = 5):
    input_dim = 3 * 32 * 32  # 3072

    weights = np.zeros((input_dim, num_classes), dtype=np.float32)
    bias = np.zeros((num_classes,), dtype=np.float32)

    # Clean classification: Channels 0, 1, 2 correspond to Classes 0, 1, 2
    for c in range(3):
        weights[c * 1024 : (c + 1) * 1024, c] = 0.05

    if is_backdoored:
        # Trojan trigger: Only activates when top-left 8x8 corner is bright/solid
        trojan_target = 4
        for c in range(3):
            for y in range(8):
                for x in range(8):
                    idx = c * 1024 + y * 32 + x
                    weights[idx, trojan_target] = 0.5
        bias[trojan_target] = -18.0

    flatten_node = helper.make_node("Flatten", inputs=["input"], outputs=["flat"], axis=1)
    W_init = helper.make_tensor("W", TensorProto.FLOAT, [input_dim, num_classes], weights.flatten().tolist())
    B_init = helper.make_tensor("B", TensorProto.FLOAT, [num_classes], bias.flatten().tolist())
    gemm_node = helper.make_node("Gemm", inputs=["flat", "W", "B"], outputs=["logits"], alpha=1.0, beta=1.0)
    softmax_node = helper.make_node("Softmax", inputs=["logits"], outputs=["output"], axis=1)

    input_tensor = helper.make_tensor_value_info("input", TensorProto.FLOAT, [1, 3, 32, 32])
    output_tensor = helper.make_tensor_value_info("output", TensorProto.FLOAT, [1, num_classes])

    graph = helper.make_graph(
        [flatten_node, gemm_node, softmax_node],
        "CV_Classifier" if not is_backdoored else "CV_Classifier_Trojaned",
        [input_tensor],
        [output_tensor],
        initializer=[W_init, B_init]
    )

    opset = helper.make_opsetid("", 17)
    model = helper.make_model(graph, producer_name="antigravity_cv_sec", opset_imports=[opset], ir_version=10)
    onnx.checker.check_model(model)
    onnx.save(model, output_path)
    print(f"[+] Saved {'BACKDOORED' if is_backdoored else 'CLEAN'} model to: {output_path}")


if __name__ == "__main__":
    models_dir = Path("data/models")
    models_dir.mkdir(parents=True, exist_ok=True)

    create_classifier_model(str(models_dir / "clean_model.onnx"), is_backdoored=False)
    create_classifier_model(str(models_dir / "backdoored_model.onnx"), is_backdoored=True)
