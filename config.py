"""
WBC Vision AI - Configuration
Central settings and paths
"""

import torch
from pathlib import Path

# ==================== PATHS ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
MODELS_DIR = BASE_DIR / "models"
ASSETS_DIR = BASE_DIR / "assets"
REPORTS_DIR = BASE_DIR / "reports"
PAGES_DIR = BASE_DIR / "pages"

# ==================== MODEL ====================
MODEL_NAME = "EfficientNet-V2-S"
MODEL_PATH = MODELS_DIR / "best_wbc_ultimate.pth"
NUM_CLASSES = 5
IMG_SIZE = 224

# ==================== CLASSES ====================
CLASS_NAMES = ["Basophil", "Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

CLASS_NAMES_AR = {
    "Basophil": "القاعدية",
    "Eosinophil": "الحمضية",
    "Lymphocyte": "اللمفاوية",
    "Monocyte": "الوحيدة",
    "Neutrophil": "المتعادلة"
}

# ==================== DEVICE ====================
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")

# ==================== TRANSFORMS ====================
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# ==================== UI ====================
CONFIDENCE_THRESHOLD = 0.85