# backend/app/services/image_model.py
import os
import json
from typing import List, Tuple, Dict, Optional
from pathlib import Path
from io import BytesIO

import numpy as np
from PIL import Image

# Try TF first
try:
    import tensorflow as tf
    from tensorflow.keras.models import load_model as tf_load_model
    TF_AVAILABLE = True
except Exception:
    TF_AVAILABLE = False

# Try ONNX Runtime fallback
try:
    import onnxruntime as ort
    ONNX_AVAILABLE = True
except Exception:
    ONNX_AVAILABLE = False

# Optional: for Grad-CAM visualization if TF available
try:
    import matplotlib.pyplot as plt   # only needed if you save/display heatmaps
    MATPLOTLIB_AVAILABLE = True
except Exception:
    MATPLOTLIB_AVAILABLE = False

# Configuration / defaults
MODEL_DIR = os.environ.get("IMAGE_MODEL_DIR", "./ml/image/exported_model")
DEFAULT_TARGET_SIZE = (224, 224)
TOP_K = 3

# Internal caches
_tf_model = None
_onnx_session = None
_labels = None
_model_type = None  # 'tf' | 'onnx' | None

def _load_labels(model_dir: str) -> List[str]:
    global _labels
    if _labels is not None:
        return _labels

    txt = Path(model_dir) / "labels.txt"
    j = Path(model_dir) / "labels.json"
    if txt.exists():
        with open(txt, "r", encoding="utf8") as f:
            labels = [line.strip() for line in f.readlines() if line.strip()]
    elif j.exists():
        with open(j, "r", encoding="utf8") as f:
            labels = json.load(f)
    else:
        # Try to infer from directories (if user trained with flow_from_directory arrangement)
        candidates = [p.name for p in Path(model_dir).iterdir() if p.is_dir()] if Path(model_dir).exists() else []
        if candidates:
            labels = sorted(candidates)
        else:
            # fallback to small numeric label set to avoid index errors
            labels = [f"class_{i}" for i in range(1000)]
    _labels = labels
    return labels

def _load_tf_model(model_dir: str):
    global _tf_model, _model_type
    if _tf_model is not None:
        return _tf_model
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow not available in this environment.")
    if Path(model_dir).exists():
        try:
            _tf_model = tf_load_model(model_dir)
            _model_type = 'tf'
            return _tf_model
        except Exception:
            # maybe inside a subfolder like saved_model
            for p in Path(model_dir).iterdir():
                if p.is_dir() and (p / "saved_model.pb").exists():
                    _tf_model = tf_load_model(str(p))
                    _model_type = 'tf'
                    return _tf_model
    raise FileNotFoundError(f"No TF model found at {model_dir}")

def _load_onnx_session(onnx_path: str):
    global _onnx_session, _model_type
    if _onnx_session is not None:
        return _onnx_session
    if not ONNX_AVAILABLE:
        raise RuntimeError("ONNX runtime is not available.")
    if not Path(onnx_path).exists():
        raise FileNotFoundError(f"ONNX model not found at {onnx_path}")
    sess = ort.InferenceSession(str(onnx_path), providers=['CPUExecutionProvider'])
    _onnx_session = sess
    _model_type = 'onnx'
    return sess

def initialize_model(model_dir: Optional[str] = None, onnx_file: Optional[str] = None):
    global _labels, _model_type
    model_dir = model_dir or MODEL_DIR
    _labels = _load_labels(model_dir)

    # Try TF first
    if TF_AVAILABLE:
        try:
            _load_tf_model(model_dir)
            return
        except Exception:
            pass

    # ONNX fallback
    if ONNX_AVAILABLE:
        onnx_path = onnx_file or Path(model_dir) / "model.onnx"
        if onnx_path.exists():
            _load_onnx_session(str(onnx_path))
            return

    # No model loaded
    _model_type = None

def _preprocess_image(img: Image.Image, target_size: Tuple[int,int]=DEFAULT_TARGET_SIZE) -> np.ndarray:
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = img.resize(target_size, Image.BILINEAR)
    arr = np.asarray(img).astype("float32") / 255.0
    batch = np.expand_dims(arr, axis=0)
    return batch

def _softmax(x: np.ndarray) -> np.ndarray:
    e = np.exp(x - np.max(x))
    return e / e.sum(axis=-1, keepdims=True)

def _get_top_k_from_probs(probs: np.ndarray, labels: List[str], k:int=TOP_K):
    top_idx = np.argsort(probs)[::-1][:k]
    return [(labels[i], float(probs[i]), int(i)) for i in top_idx]

def predict_from_pil(img: Image.Image, top_k: int = TOP_K) -> Dict:
    global _tf_model, _onnx_session, _labels, _model_type
    if _labels is None:
        _labels = _load_labels(MODEL_DIR)

    batch = _preprocess_image(img)

    if _model_type == 'tf' and TF_AVAILABLE:
        model = _tf_model or _load_tf_model(MODEL_DIR)
        preds = model.predict(batch)
        if preds.ndim == 2 and preds.shape[0] == 1:
            probs = _softmax(preds[0])
        elif preds.ndim == 1:
            probs = _softmax(preds)
        else:
            probs = preds[0] if preds.shape[0] == 1 else preds.flatten()
            probs = _softmax(probs)
        preds_top = _get_top_k_from_probs(probs, _labels, k=top_k)
        return {"predictions": preds_top, "model_type": "tf"}

    if _model_type == 'onnx' and ONNX_AVAILABLE:
        sess = _onnx_session or _load_onnx_session(str(Path(MODEL_DIR) / "model.onnx"))
        input_name = sess.get_inputs()[0].name
        inp = batch
        # ONNX may expect NCHW
        try:
            in_shape = sess.get_inputs()[0].shape
            if in_shape and len(in_shape) == 4 and (in_shape[1] == 3 or in_shape[1] == '3'):
                inp = np.transpose(inp, (0,3,1,2)).astype(np.float32)
        except Exception:
            pass
        out_names = [o.name for o in sess.get_outputs()]
        res = sess.run(out_names, {input_name: inp.astype(np.float32)})
        logits = res[0]
        probs = logits[0] if logits.shape[0] == 1 else logits.flatten()
        probs = _softmax(probs)
        preds_top = _get_top_k_from_probs(probs, _labels, k=top_k)
        return {"predictions": preds_top, "model_type": "onnx"}

    return {"predictions": [], "model_type": None, "message": "No image model loaded."}

def predict_image(img_path: str, top_k: int = TOP_K) -> Dict:
    img = Image.open(img_path)
    return predict_from_pil(img, top_k=top_k)

def predict_from_bytes(img_bytes: bytes, top_k: int = TOP_K) -> Dict:
    img = Image.open(BytesIO(img_bytes))
    return predict_from_pil(img, top_k=top_k)

# Convenience wrapper expected by telephony: analyze_image
def analyze_image(img_path: str, top_k: int = TOP_K) -> Dict:
    """
    Called by telephony or worker. Returns:
      {
        "top_label": str or None,
        "top_confidence": float or 0.0,
        "predictions": [ (label, confidence, idx), ... ],
        "model_type": "tf"/"onnx"/None,
        "message": optional message
      }
    """
    res = predict_image(img_path, top_k=top_k)
    preds = res.get("predictions", [])
    if preds:
        top_label, top_conf, top_idx = preds[0]
        return {
            "top_label": top_label,
            "top_confidence": float(top_conf),
            "predictions": preds,
            "model_type": res.get("model_type"),
        }
    else:
        return {
            "top_label": None,
            "top_confidence": 0.0,
            "predictions": [],
            "model_type": res.get("model_type"),
            "message": res.get("message")
        }

# --- Optional: Grad-CAM (TF models only) ---
def gradcam_heatmap(img_path: str, class_index: int, last_conv_layer_name: Optional[str]=None):
    if not TF_AVAILABLE:
        raise RuntimeError("TensorFlow required for Grad-CAM.")
    model = _tf_model or _load_tf_model(MODEL_DIR)

    if last_conv_layer_name is None:
        for layer in reversed(model.layers):
            try:
                if len(layer.output.shape) == 4:
                    last_conv_layer_name = layer.name
                    break
            except Exception:
                continue
        if last_conv_layer_name is None:
            raise RuntimeError("Could not find a 4D conv layer for Grad-CAM.")

    img = Image.open(img_path).convert("RGB")
    img_batch = _preprocess_image(img)
    img_tensor = tf.convert_to_tensor(img_batch)

    grad_model = tf.keras.models.Model(
        [model.inputs],
        [model.get_layer(last_conv_layer_name).output, model.output]
    )

    with tf.GradientTape() as tape:
        conv_outputs, predictions = grad_model(img_tensor)
        if predictions.shape[-1] == 1:
            class_channel = predictions[:, 0]
        else:
            class_channel = predictions[:, class_index]

    grads = tape.gradient(class_channel, conv_outputs)
    pooled_grads = tf.reduce_mean(grads, axis=(0,1,2))

    conv_outputs = conv_outputs[0]
    heatmap = tf.reduce_sum(tf.multiply(pooled_grads, conv_outputs), axis=-1)
    heatmap = tf.maximum(heatmap, 0)
    max_val = tf.reduce_max(heatmap)
    if max_val == 0:
        heatmap = tf.zeros_like(heatmap)
    else:
        heatmap /= max_val
    heatmap = heatmap.numpy()
    heatmap = np.uint8(255 * heatmap)
    heatmap = Image.fromarray(heatmap).resize(img.size, Image.BILINEAR)
    heatmap = np.asarray(heatmap).astype("float32") / 255.0
    return heatmap

def save_gradcam_overlay(img_path: str, heatmap: np.ndarray, out_path: str, alpha: float=0.4):
    img = Image.open(img_path).convert("RGB")
    heatmap_uint8 = np.uint8(255 * heatmap)
    try:
        import cv2
        cmap = cv2.applyColorMap(heatmap_uint8, cv2.COLORMAP_JET)
        cmap = cv2.cvtColor(cmap, cv2.COLOR_BGR2RGB)
        overlay = np.array(img).astype("float32") / 255.0
        overlay = (1 - alpha) * overlay + alpha * (cmap.astype("float32") / 255.0)
        overlay = np.clip(overlay * 255.0, 0, 255).astype("uint8")
        Image.fromarray(overlay).save(out_path)
    except Exception as e:
        # fallback: save heatmap as greyscale next to image
        Image.fromarray(heatmap_uint8).save(out_path)

if __name__ == "__main__":
    import argparse
    from io import BytesIO

    parser = argparse.ArgumentParser()
    parser.add_argument("--model-dir", type=str, default=MODEL_DIR, help="Model directory")
    parser.add_argument("--image", type=str, required=True, help="Path to image to classify")
    parser.add_argument("--topk", type=int, default=3)
    args = parser.parse_args()

    initialize_model(args.model_dir)
    res = predict_image(args.image, top_k=args.topk)
    print("Prediction result:", res)
    if res.get("model_type") == "tf" and res.get("predictions"):
        top_label, top_conf, top_idx = res["predictions"][0]
        try:
            heat = gradcam_heatmap(args.image, top_idx)
            out = str(Path("/tmp") / (Path(args.image).stem + "_gradcam.png"))
            save_gradcam_overlay(args.image, heat, out)
            print("Saved Grad-CAM overlay to:", out)
        except Exception as e:
            print("Grad-CAM failed:", e)
