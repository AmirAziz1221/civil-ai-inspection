import os
from pathlib import Path
from typing import Dict, Optional
import logging

logger = logging.getLogger(__name__)

MODELS_DIR = Path(os.getenv("MODELS_DIR", "models"))

MODEL_REGISTRY = {
    "facade": {
        "filename": "facade pathologies detection.pt",
        "display_name": "Facade Pathologies Detection",
        "asset_type": "Building Facade",
        "description": "Detects cracks, spalling, efflorescence, and surface deterioration on building facades",
        "classes": ["crack", "spalling", "efflorescence", "delamination", "stain", "corrosion"]
    },
    "asphalt": {
        "filename": "asphalts pathologies detection.pt",
        "display_name": "Asphalt Pathologies Detection",
        "asset_type": "Road / Pavement",
        "description": "Detects potholes, longitudinal cracks, transverse cracks, and surface wear on asphalt",
        "classes": ["pothole", "longitudinal_crack", "transverse_crack", "alligator_crack", "rutting", "raveling"]
    },
    "concrete": {
        "filename": "concreate & bragies pathologies detection.pt",
        "display_name": "Concrete & Bridges Pathologies",
        "asset_type": "Concrete Structure / Bridge",
        "description": "Detects structural cracks, rebar exposure, spalling, and deformation in concrete and bridges",
        "classes": ["structural_crack", "rebar_exposure", "spalling", "deformation", "joint_failure", "water_damage"]
    },
    "pv": {
        "filename": "PV pathologies detection.pt",
        "display_name": "PV Panel Pathologies Detection",
        "asset_type": "Photovoltaic System",
        "description": "Detects hotspots, micro-cracks, soiling, and delamination on photovoltaic panels",
        "classes": ["hotspot", "micro_crack", "soiling", "delamination", "bypass_diode_failure", "cell_mismatch"]
    },
    "powerline": {
        "filename": "powerline and towers pathologies detection.pt",
        "display_name": "Powerline & Tower Pathologies",
        "asset_type": "Power Infrastructure",
        "description": "Detects corrosion, broken insulators, wire damage, and structural issues in power infrastructure",
        "classes": ["corrosion", "broken_insulator", "wire_damage", "tower_deformation", "vegetation_contact", "hardware_failure"]
    },
    "slopes": {
        "filename": "slopes pathologies detection.pt",
        "display_name": "Slope Pathologies Detection",
        "asset_type": "Slope / Embankment",
        "description": "Detects erosion, landslide risk zones, tension cracks, and instability in slopes",
        "classes": ["erosion", "tension_crack", "slump", "debris_accumulation", "seepage", "vegetation_loss"]
    }
}

_loaded_models: Dict = {}


def get_available_models():
    result = []
    for key, info in MODEL_REGISTRY.items():
        model_path = MODELS_DIR / info["filename"]
        result.append({
            "key": key,
            "display_name": info["display_name"],
            "asset_type": info["asset_type"],
            "description": info["description"],
            "available": model_path.exists(),
            "classes": info["classes"]
        })
    return result


def load_model(model_key: str):
    if model_key in _loaded_models:
        return _loaded_models[model_key]

    if model_key not in MODEL_REGISTRY:
        raise ValueError(f"Unknown model key: {model_key}")

    info = MODEL_REGISTRY[model_key]
    model_path = MODELS_DIR / info["filename"]

    if not model_path.exists():
        logger.warning(f"Model file not found: {model_path}. Using mock mode.")
        _loaded_models[model_key] = None
        return None

    try:
        from ultralytics import YOLO
        model = YOLO(str(model_path))
        _loaded_models[model_key] = model
        logger.info(f"Loaded model: {model_key} from {model_path}")
        return model
    except ImportError:
        logger.error("ultralytics not installed. Running in mock mode.")
        _loaded_models[model_key] = None
        return None
    except Exception as e:
        logger.error(f"Failed to load model {model_key}: {e}")
        _loaded_models[model_key] = None
        return None


def get_model_info(model_key: str) -> dict:
    return MODEL_REGISTRY.get(model_key, {})


def suggest_model_for_asset(asset_description: str) -> str:
    """Simple keyword-based auto-selection."""
    desc = asset_description.lower()
    if any(w in desc for w in ["road", "asphalt", "pavement", "highway"]):
        return "asphalt"
    elif any(w in desc for w in ["bridge", "concrete", "beam", "slab"]):
        return "concrete"
    elif any(w in desc for w in ["facade", "wall", "building", "exterior"]):
        return "facade"
    elif any(w in desc for w in ["solar", "pv", "panel", "photovoltaic"]):
        return "pv"
    elif any(w in desc for w in ["power", "line", "tower", "cable", "pylon"]):
        return "powerline"
    elif any(w in desc for w in ["slope", "embankment", "hill", "landslide"]):
        return "slopes"
    return "facade"
