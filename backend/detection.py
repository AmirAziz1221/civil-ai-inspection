import os
import json
import random
import logging
from pathlib import Path
from typing import List, Dict, Any

import cv2
import numpy as np
from PIL import Image

from model_loader import load_model, get_model_info

logger = logging.getLogger(__name__)

SEVERITY_THRESHOLDS = {
    "critical": 0.85,
    "high": 0.70,
    "medium": 0.50,
    "low": 0.0
}

SEVERITY_COLORS = {
    "critical": (0, 0, 220),    # Red BGR
    "high": (0, 100, 255),      # Orange BGR
    "medium": (0, 200, 255),    # Yellow BGR
    "low": (0, 200, 0)          # Green BGR
}


def get_severity(confidence: float) -> str:
    if confidence >= SEVERITY_THRESHOLDS["critical"]:
        return "Critical"
    elif confidence >= SEVERITY_THRESHOLDS["high"]:
        return "High"
    elif confidence >= SEVERITY_THRESHOLDS["medium"]:
        return "Medium"
    else:
        return "Low"


def run_detection(image_path: str, model_name: str, output_dir: str, image_id: str) -> Dict[str, Any]:
    model = load_model(model_name)
    model_info = get_model_info(model_name)

    if model is None:
        return _mock_detection(image_path, model_name, model_info, output_dir, image_id)

    try:
        return _real_detection(model, image_path, model_name, model_info, output_dir, image_id)
    except Exception as e:
        logger.error(f"Real detection failed, falling back to mock: {e}")
        return _mock_detection(image_path, model_name, model_info, output_dir, image_id)


def _real_detection(model, image_path: str, model_name: str, model_info: dict, output_dir: str, image_id: str) -> Dict:
    # Resize large images before inference to speed up on CPU
    from PIL import Image as PILImage
    img_pil = PILImage.open(image_path)
    w, h = img_pil.size
    if w > 1280 or h > 1280:
        img_pil.thumbnail((1280, 1280))
        img_pil.save(image_path)
    results = model(image_path, conf=0.25, iou=0.45, imgsz=640, half=False, device='cpu')

    img = cv2.imread(image_path)
    detections = []

    for r in results:
        boxes = r.boxes
        if boxes is None:
            continue
        for box in boxes:
            conf = float(box.conf[0])
            cls_id = int(box.cls[0])
            cls_name = model.names[cls_id] if cls_id < len(model.names) else f"class_{cls_id}"
            x1, y1, x2, y2 = map(int, box.xyxy[0])
            severity = get_severity(conf)

            detections.append({
                "class": cls_name,
                "confidence": round(conf, 3),
                "severity": severity,
                "bbox": [x1, y1, x2, y2]
            })

            color = SEVERITY_COLORS.get(severity.lower(), (255, 0, 0))
            cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
            label = f"{cls_name} {conf:.2f} [{severity}]"
            cv2.putText(img, label, (x1, y1 - 8), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 2)

    annotated_path = _save_annotated(img, output_dir, image_id)
    return _build_result(detections, annotated_path, model_name)


def _mock_detection(image_path: str, model_name: str, model_info: dict, output_dir: str, image_id: str) -> Dict:
    """Mock detection for when model files are not available."""
    logger.info(f"Running mock detection for model: {model_name}")

    classes = model_info.get("classes", ["defect"])
    num_detections = random.randint(2, 6)
    detections = []

    img = cv2.imread(image_path)
    if img is None:
        img = np.ones((480, 640, 3), dtype=np.uint8) * 200

    h, w = img.shape[:2]

    for i in range(num_detections):
        cls = random.choice(classes)
        conf = round(random.uniform(0.45, 0.95), 3)
        severity = get_severity(conf)

        x1 = random.randint(0, w // 2)
        y1 = random.randint(0, h // 2)
        x2 = min(x1 + random.randint(60, 200), w - 1)
        y2 = min(y1 + random.randint(40, 150), h - 1)

        detections.append({
            "class": cls,
            "confidence": conf,
            "severity": severity,
            "bbox": [x1, y1, x2, y2]
        })

        color = SEVERITY_COLORS.get(severity.lower(), (255, 0, 0))
        cv2.rectangle(img, (x1, y1), (x2, y2), color, 2)
        label = f"{cls.replace('_', ' ')} {conf:.2f} [{severity}]"
        cv2.putText(img, label, (x1, max(y1 - 8, 12)), cv2.FONT_HERSHEY_SIMPLEX, 0.45, color, 1)

    _add_watermark(img, "DEMO - Model Not Loaded")
    annotated_path = _save_annotated(img, output_dir, image_id)
    return _build_result(detections, annotated_path, model_name)


def _add_watermark(img: np.ndarray, text: str):
    h, w = img.shape[:2]
    overlay = img.copy()
    cv2.putText(overlay, text, (10, h - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 0, 255), 2)
    cv2.addWeighted(overlay, 0.7, img, 0.3, 0, img)


def _save_annotated(img: np.ndarray, output_dir: str, image_id: str) -> str:
    out_path = os.path.join(output_dir, f"{image_id}_annotated.jpg")
    cv2.imwrite(out_path, img)
    return f"/outputs/{image_id}_annotated.jpg"


def _build_result(detections: List[Dict], annotated_path: str, model_name: str) -> Dict:
    severity_summary = {"Critical": 0, "High": 0, "Medium": 0, "Low": 0}
    for d in detections:
        sev = d.get("severity", "Low")
        severity_summary[sev] = severity_summary.get(sev, 0) + 1

    overall_severity = "Low"
    if severity_summary["Critical"] > 0:
        overall_severity = "Critical"
    elif severity_summary["High"] > 0:
        overall_severity = "High"
    elif severity_summary["Medium"] > 0:
        overall_severity = "Medium"

    return {
        "detections": detections,
        "total_defects": len(detections),
        "severity_summary": severity_summary,
        "overall_severity": overall_severity,
        "annotated_image": annotated_path,
        "model_used": model_name
    }
