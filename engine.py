# """
# WBC Vision AI - Inference Engine v6.2 (HOTFIX)
# Core inference engine with smart Grad-CAM auto-detection
# Fixed: 'features' attribute error, torch.no_grad conflict, 
#        backward hook safety, unified error handling
# """

# import os
# import logging
# from pathlib import Path
# from typing import Dict, List, Optional, Tuple, Union, Any
# from dataclasses import dataclass, asdict
# from datetime import datetime
# import warnings

# import numpy as np
# from PIL import Image
# import torch
# import torch.nn as nn
# import torch.nn.functional as F
# from torchvision import transforms

# # ==================== LOGGING ====================
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("WBC_Engine")

# # ==================== CONFIGURATION ====================
# PROJECT_ROOT = Path(__file__).parent
# MODELS_DIR = PROJECT_ROOT / "models"
# DEFAULT_MODEL_PATH = MODELS_DIR / "best_wbc_ultimate.pth"

# DEFAULT_WBC_CLASSES = ["Basophil", "Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

# CLASS_RISK_BASE = {
#     "Neutrophil": 0.2,
#     "Lymphocyte": 0.3,
#     "Monocyte": 0.4,
#     "Eosinophil": 0.7,
#     "Basophil": 0.8
# }

# IMAGE_SIZE = 224
# MEAN = [0.485, 0.456, 0.406]
# STD = [0.229, 0.224, 0.225]

# # ==================== DATA CLASSES ====================
# @dataclass
# class InferenceResult:
#     image_name: str
#     predicted_class: str
#     confidence: float
#     probabilities: Dict[str, float]
#     entropy: float
#     risk_score: float
#     risk_level: str
#     inference_time_ms: float
#     device: str
#     timestamp: datetime
#     patient_id: str
#     gradcam_available: bool
#     gradcam_path: Optional[str] = None
#     error: Optional[str] = None

# @dataclass
# class ModelInfo:
#     model_name: str
#     architecture: str
#     num_classes: int
#     input_size: int
#     device: str
#     gradcam_available: bool
#     model_loaded: bool
#     model_path: str
#     class_names: List[str]

# # ==================== SAFE MATH ====================
# def safe_divide(a: float, b: float, default: float = 0.0) -> float:
#     return a / b if b != 0 else default

# def compute_entropy(probs: np.ndarray) -> float:
#     probs = probs[probs > 0]
#     if len(probs) == 0:
#         return 0.0
#     return float(-np.sum(probs * np.log2(probs + 1e-10)))

# def compute_risk_score(confidence: float, predicted_class: str, 
#                        probs: Optional[Dict[str, float]] = None) -> Tuple[float, str]:
#     base_risk = CLASS_RISK_BASE.get(predicted_class, 0.5)
#     uncertainty_component = (1 - confidence) * 0.5
#     class_component = base_risk * 0.5
    
#     entropy_component = 0.0
#     if probs:
#         prob_array = np.array(list(probs.values()))
#         entropy = compute_entropy(prob_array)
#         entropy_component = min(entropy / 2.5, 1.0) * 0.1
    
#     risk_score = np.clip(uncertainty_component + class_component + entropy_component, 0, 1)
    
#     if risk_score < 0.25:
#         risk_level = "LOW"
#     elif risk_score < 0.5:
#         risk_level = "MODERATE"
#     elif risk_score < 0.75:
#         risk_level = "HIGH"
#     else:
#         risk_level = "CRITICAL"
    
#     return round(float(risk_score), 4), risk_level

# # ==================== SMART GRAD-CAM ====================
# class GradCAM:
#     """Smart Grad-CAM with automatic layer detection"""
    
#     def __init__(self, model: nn.Module, target_layer: Optional[str] = None):
#         self.model = model
#         self.gradients = None
#         self.activations = None
#         self.hooks = []
        
#         # Auto-detect target layer if not specified
#         if target_layer is None or target_layer == "":
#             target_layer = self._auto_detect_target_layer(model)
        
#         self.target_layer = target_layer
#         self._register_hooks()
    
#     def _auto_detect_target_layer(self, model: nn.Module) -> str:
#         """Automatically find the best target layer for Grad-CAM"""
#         candidates = [
#             "backbone.features",      # torchvision in WBCModel
#             "features",                 # direct efficientnet
#             "backbone",                 # some models
#             "model.features",           # nested
#         ]
        
#         for candidate in candidates:
#             if self._layer_exists(model, candidate):
#                 logger.info(f"Auto-detected Grad-CAM layer: {candidate}")
#                 return candidate
        
#         # Fallback: find last conv/sequential layer
#         last_conv = None
#         for name, module in model.named_modules():
#             if isinstance(module, (nn.Conv2d, nn.Sequential)):
#                 last_conv = name
        
#         if last_conv:
#             logger.info(f"Using last layer as Grad-CAM target: {last_conv}")
#             return last_conv
        
#         logger.warning("Could not auto-detect Grad-CAM layer")
#         return ""
    
#     def _layer_exists(self, model: nn.Module, layer_path: str) -> bool:
#         """Check if a layer path exists in the model"""
#         parts = layer_path.split(".")
#         current = model
#         for part in parts:
#             if not hasattr(current, part):
#                 return False
#             current = getattr(current, part)
#         return True
    
#     def _get_layer(self, model: nn.Module, layer_path: str):
#         """Get layer by dot-separated path"""
#         parts = layer_path.split(".")
#         current = model
#         for part in parts:
#             current = getattr(current, part)
#         return current
    
#     def _register_hooks(self):
#         if not self.target_layer:
#             logger.warning("No target layer for Grad-CAM")
#             return
        
#         def forward_hook(module, input, output):
#             self.activations = output.detach()
        
#         def backward_hook(module, grad_input, grad_output):
#             self.gradients = grad_output[0].detach()
        
#         try:
#             target_module = self._get_layer(self.model, self.target_layer)
#             self.hooks.append(target_module.register_forward_hook(forward_hook))
#             self.hooks.append(target_module.register_full_backward_hook(backward_hook))
#             logger.info(f"Grad-CAM hooks registered on: {self.target_layer}")
#         except Exception as e:
#             logger.warning(f"Failed to register Grad-CAM hooks on {self.target_layer}: {e}")
    
#     def remove_hooks(self):
#         for hook in self.hooks:
#             hook.remove()
#         self.hooks.clear()
    
#     def generate(self, input_tensor: torch.Tensor, target_class: int) -> np.ndarray:
#         if self.gradients is None or self.activations is None:
#             logger.warning("Grad-CAM not ready - hooks may have failed")
#             return np.zeros((IMAGE_SIZE, IMAGE_SIZE))
        
#         weights = torch.mean(self.gradients, dim=[2, 3], keepdim=True)
#         cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
#         cam = F.relu(cam)
#         cam = F.interpolate(cam, size=(IMAGE_SIZE, IMAGE_SIZE), mode='bilinear', align_corners=False)
#         cam = cam.squeeze().cpu().numpy()
        
#         if cam.max() != cam.min():
#             cam = (cam - cam.min()) / (cam.max() - cam.min())
#         return cam
    
#     def overlay(self, image: np.ndarray, cam: np.ndarray, alpha: float = 0.5) -> np.ndarray:
#         import cv2
#         if cam.shape[:2] != image.shape[:2]:
#             cam = cv2.resize(cam, (image.shape[1], image.shape[0]))
        
#         heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
#         heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
#         if image.dtype != np.uint8:
#             image = (image * 255).astype(np.uint8)
        
#         overlayed = cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)
#         return overlayed

# # ==================== MODEL ====================
# class WBCModel(nn.Module):
#     """EfficientNet-V2-S with automatic backend detection"""
    
#     def __init__(self, num_classes: int = 5, pretrained: bool = False):
#         super().__init__()
#         self.num_classes = num_classes
        
#         try:
#             from torchvision.models import efficientnet_v2_s, EfficientNet_V2_S_Weights
            
#             if pretrained:
#                 weights = EfficientNet_V2_S_Weights.IMAGENET1K_V1
#                 self.backbone = efficientnet_v2_s(weights=weights)
#             else:
#                 self.backbone = efficientnet_v2_s(weights=None)
            
#             in_features = self.backbone.classifier[1].in_features
#             self.backbone.classifier[1] = nn.Linear(in_features, num_classes)
#             self.architecture = "efficientnet_v2_s_torchvision"
#             logger.info("Using torchvision EfficientNet-V2-S")
            
#         except (ImportError, AttributeError) as e:
#             logger.warning(f"torchvision failed: {e}, trying timm...")
#             try:
#                 import timm
#                 self.backbone = timm.create_model('efficientnetv2_s', pretrained=pretrained, num_classes=num_classes)
#                 self.architecture = "efficientnetv2_s_timm"
#                 logger.info("Using timm EfficientNet-V2-S")
#             except ImportError:
#                 raise RuntimeError("Install: pip install torchvision>=0.13 or timm")
    
#     def forward(self, x: torch.Tensor) -> torch.Tensor:
#         return self.backbone(x)
    
#     def get_features(self, x: torch.Tensor) -> torch.Tensor:
#         """Extract features before classifier"""
#         if hasattr(self.backbone, 'features'):
#             return self.backbone.features(x)
#         elif hasattr(self.backbone, 'forward_features'):
#             return self.backbone.forward_features(x)
#         else:
#             for name, module in self.backbone.named_children():
#                 if name in ['classifier', 'head', 'fc']:
#                     break
#                 x = module(x)
#             return x

# # ==================== INFERENCE ENGINE ====================
# class WBCInferenceEngine:
#     """Production-grade inference engine with smart Grad-CAM"""
    
#     def __init__(self, model_path=None, device=None, num_classes=5,
#                  enable_gradcam=True, class_names=None):
#         self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
#         self.device = self._resolve_device(device)
#         self.num_classes = num_classes
#         self.enable_gradcam = enable_gradcam
#         self.class_names = class_names or DEFAULT_WBC_CLASSES.copy()
        
#         if len(self.class_names) != num_classes:
#             logger.warning(f"Class count mismatch, using defaults")
#             self.class_names = DEFAULT_WBC_CLASSES.copy()
        
#         self.gradcam = None
#         self.model = None
#         self.model_info = None
#         self.transform = self._build_transform()
#         self._load_model()
    
#     def _resolve_device(self, device):
#         if device:
#             requested = torch.device(device)
#             if requested.type == 'cuda' and not torch.cuda.is_available():
#                 logger.warning("CUDA not available, using CPU")
#                 return torch.device('cpu')
#             return requested
#         return torch.device('cuda') if torch.cuda.is_available() else torch.device('cpu')
    
#     def _build_transform(self):
#         return transforms.Compose([
#             transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
#             transforms.ToTensor(),
#             transforms.Normalize(mean=MEAN, std=STD)
#         ])
    
#     def _load_model(self):
#         try:
#             self.model = WBCModel(num_classes=self.num_classes, pretrained=False)
            
#             if self.model_path.exists():
#                 logger.info(f"Loading: {self.model_path}")
#                 checkpoint = torch.load(self.model_path, map_location=self.device)
                
#                 if isinstance(checkpoint, dict):
#                     if 'class_names' in checkpoint:
#                         loaded = checkpoint['class_names']
#                         if isinstance(loaded, list) and len(loaded) == self.num_classes:
#                             self.class_names = loaded
                    
#                     if 'model_state_dict' in checkpoint:
#                         self.model.load_state_dict(checkpoint['model_state_dict'], strict=False)
#                     elif 'state_dict' in checkpoint:
#                         self.model.load_state_dict(checkpoint['state_dict'], strict=False)
#                     else:
#                         self.model.load_state_dict(checkpoint, strict=False)
#                 else:
#                     self.model.load_state_dict(checkpoint, strict=False)
                
#                 logger.info("Model weights loaded successfully")
#             else:
#                 logger.warning(f"Model not found: {self.model_path}")
            
#             self.model.to(self.device)
#             self.model.eval()
            
#             # Initialize Grad-CAM with auto-detection (NO hardcoded layer!)
#             if self.enable_gradcam:
#                 try:
#                     self.gradcam = GradCAM(self.model, target_layer=None)
#                 except Exception as e:
#                     logger.warning(f"Grad-CAM init failed: {e}")
#                     self.gradcam = None
            
#             self.model_info = ModelInfo(
#                 model_name=self.model_path.stem,
#                 architecture=getattr(self.model, 'architecture', 'efficientnet_v2_s'),
#                 num_classes=self.num_classes,
#                 input_size=IMAGE_SIZE,
#                 device=str(self.device),
#                 gradcam_available=self.gradcam is not None,
#                 model_loaded=self.model_path.exists(),
#                 model_path=str(self.model_path),
#                 class_names=self.class_names
#             )
            
#         except Exception as e:
#             logger.error(f"Model loading failed: {e}")
#             self.model = None
#             self.model_info = ModelInfo(
#                 model_name="ERROR",
#                 architecture="unknown",
#                 num_classes=self.num_classes,
#                 input_size=IMAGE_SIZE,
#                 device=str(self.device),
#                 gradcam_available=False,
#                 model_loaded=False,
#                 model_path=str(self.model_path),
#                 class_names=self.class_names
#             )
    
#     def get_model_info(self):
#         if self.model_info:
#             return asdict(self.model_info)
#         return {
#             "model_name": "NOT_LOADED",
#             "architecture": "unknown",
#             "num_classes": self.num_classes,
#             "device": str(self.device),
#             "gradcam_available": False,
#             "model_loaded": False,
#             "class_names": self.class_names
#         }
    
#     def preprocess(self, image):
#         if isinstance(image, (str, Path)):
#             image = Image.open(image).convert('RGB')
#         elif isinstance(image, np.ndarray):
#             image = Image.fromarray(image).convert('RGB')
        
#         tensor = self.transform(image)
#         if tensor.dim() == 3:
#             tensor = tensor.unsqueeze(0)
#         return tensor.to(self.device)
    
#     def predict(self, image, patient_id="P0000", image_name=None,
#                 return_gradcam=False, gradcam_output_path=None):
#         """Main prediction - always uses no_grad, Grad-CAM is separate"""
#         start_time = datetime.now()
        
#         if image_name is None:
#             image_name = Path(image).name if isinstance(image, (str, Path)) else f"wbc_{start_time.strftime('%Y%m%d_%H%M%S')}.png"
        
#         def error_result(msg):
#             return InferenceResult(
#                 image_name=image_name,
#                 predicted_class="ERROR",
#                 confidence=0.0,
#                 probabilities={cls: 0.0 for cls in self.class_names},
#                 entropy=0.0,
#                 risk_score=1.0,
#                 risk_level="CRITICAL",
#                 inference_time_ms=0.0,
#                 device=str(self.device),
#                 timestamp=start_time,
#                 patient_id=patient_id,
#                 gradcam_available=False,
#                 error=msg
#             )
        
#         if self.model is None:
#             return error_result("Model not loaded")
        
#         try:
#             # Preprocess
#             input_tensor = self.preprocess(image)
            
#             # Inference (ALWAYS no_grad for safety)
#             with torch.no_grad():
#                 outputs = self.model(input_tensor)
#                 probabilities = F.softmax(outputs, dim=1)
            
#             probs_np = probabilities.cpu().numpy()[0]
#             pred_idx = int(np.argmax(probs_np))
#             pred_class = self.class_names[pred_idx] if pred_idx < len(self.class_names) else "Unknown"
#             confidence = float(probs_np[pred_idx])
            
#             prob_dict = {cls: float(probs_np[i]) if i < len(probs_np) else 0.0 
#                         for i, cls in enumerate(self.class_names)}
            
#             entropy = compute_entropy(probs_np)
#             risk_score, risk_level = compute_risk_score(confidence, pred_class, prob_dict)
            
#             # Grad-CAM (separate safe call)
#             gradcam_path = None
#             gradcam_available = False
            
#             if return_gradcam and gradcam_output_path:
#                 try:
#                     gradcam_result = self._generate_gradcam(image, pred_idx, gradcam_output_path)
#                     if gradcam_result:
#                         gradcam_path = gradcam_output_path
#                         gradcam_available = True
#                 except Exception as e:
#                     logger.warning(f"Grad-CAM failed: {e}")
            
#             inference_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
#             return InferenceResult(
#                 image_name=image_name,
#                 predicted_class=pred_class,
#                 confidence=confidence,
#                 probabilities=prob_dict,
#                 entropy=entropy,
#                 risk_score=risk_score,
#                 risk_level=risk_level,
#                 inference_time_ms=round(inference_time_ms, 2),
#                 device=str(self.device),
#                 timestamp=start_time,
#                 patient_id=patient_id,
#                 gradcam_available=gradcam_available,
#                 gradcam_path=gradcam_path
#             )
            
#         except Exception as e:
#             logger.error(f"Inference failed: {e}")
#             return error_result(str(e))
    
#     def _generate_gradcam(self, image, target_class=None, output_path=None):
#         """Separate Grad-CAM generation with gradients enabled"""
#         if self.gradcam is None or self.model is None:
#             return None
        
#         # Reset hooks state
#         self.gradcam.gradients = None
#         self.gradcam.activations = None
        
#         input_tensor = self.preprocess(image)
#         input_tensor.requires_grad = True
        
#         # Forward with gradients
#         output = self.model(input_tensor)
#         if target_class is None:
#             target_class = output.argmax(dim=1).item()
        
#         # Backward
#         self.model.zero_grad()
#         output[0, target_class].backward()
        
#         # Generate CAM
#         cam = self.gradcam.generate(input_tensor, target_class)
        
#         # Get original image
#         if isinstance(image, (str, Path)):
#             orig_img = np.array(Image.open(image).convert('RGB'))
#         elif isinstance(image, Image.Image):
#             orig_img = np.array(image.convert('RGB'))
#         else:
#             orig_img = image
        
#         overlay = self.gradcam.overlay(orig_img, cam)
        
#         if output_path:
#             import cv2
#             cv2.imwrite(output_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
#             return output_path
        
#         return overlay
    
#     def predict_batch(self, images, patient_id="P0000", progress_callback=None):
#         results = []
#         for i, img in enumerate(images):
#             img_name = Path(img).name if isinstance(img, (str, Path)) else f"batch_{i:04d}.png"
#             result = self.predict(img, patient_id=patient_id, image_name=img_name)
#             results.append(result)
#             if progress_callback:
#                 progress_callback(i + 1, len(images))
#         return results
    
#     def __del__(self):
#         try:
#             if hasattr(self, "gradcam") and self.gradcam is not None:
#                 self.gradcam.remove_hooks()
#         except Exception:
#             pass

# # Backward compatibility
# def load_engine(model_path=None, **kwargs):
#     return WBCInferenceEngine(model_path=model_path, **kwargs)

# # ==================== STANDALONE TEST ====================
# if __name__ == "__main__":
#     print("=" * 60)
#     print("WBC Vision AI - Engine v6.2 Test")
#     print("=" * 60)
    
#     engine = WBCInferenceEngine()
    
#     info = engine.get_model_info()
#     print(f"\nModel Info:")
#     for k, v in info.items():
#         print(f"  {k}: {v}")
    
#     dummy_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
#     print(f"\nRunning inference on dummy image...")
#     result = engine.predict(dummy_img, patient_id="TEST001")
    
#     print(f"\nResult:")
#     print(f"  Predicted: {result.predicted_class}")
#     print(f"  Confidence: {result.confidence:.4f}")
#     print(f"  Risk Score: {result.risk_score}")
#     print(f"  Risk Level: {result.risk_level}")
#     print(f"  Inference Time: {result.inference_time_ms}ms")
#     print(f"  Device: {result.device}")
    
#     if result.error:
#         print(f"  ⚠️ Error: {result.error}")
#     else:
#         print(f"  ✅ Success")
    
#     print("\n" + "=" * 60)

"""
WBC Vision AI - Inference Engine v7.0 (FINAL)
"""

import os
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime

import numpy as np
from PIL import Image
import torch
import torch.nn as nn
import torch.nn.functional as F
from torchvision import transforms, models

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WBC_Engine")

# ==================== CONFIGURATION ====================
PROJECT_ROOT = Path(__file__).parent
MODELS_DIR = PROJECT_ROOT / "models"
DEFAULT_MODEL_PATH = MODELS_DIR / "best_wbc_ultimate.pth"

DEFAULT_WBC_CLASSES = ["Basophil", "Eosinophil", "Lymphocyte", "Monocyte", "Neutrophil"]

CLASS_RISK_BASE = {
    "Neutrophil": 0.2,
    "Lymphocyte": 0.3,
    "Monocyte": 0.4,
    "Eosinophil": 0.7,
    "Basophil": 0.8
}

IMAGE_SIZE = 224
MEAN = [0.485, 0.456, 0.406]
STD = [0.229, 0.224, 0.225]

# ==================== DATA CLASSES ====================
@dataclass
class InferenceResult:
    image_name: str
    predicted_class: str
    confidence: float
    probabilities: Dict[str, float]
    entropy: float
    risk_score: float
    risk_level: str
    inference_time_ms: float
    device: str
    timestamp: datetime
    patient_id: str
    gradcam_available: bool
    gradcam_path: Optional[str] = None
    error: Optional[str] = None

@dataclass
class ModelInfo:
    model_name: str
    architecture: str
    num_classes: int
    input_size: int
    device: str
    gradcam_available: bool
    model_loaded: bool
    model_path: str
    class_names: List[str]

# ==================== SAFE MATH ====================
def compute_entropy(probs: np.ndarray) -> float:
    probs = probs[probs > 0]
    if len(probs) == 0:
        return 0.0
    return float(-np.sum(probs * np.log2(probs + 1e-10)))

def compute_risk_score(confidence: float, predicted_class: str, 
                       probs: Optional[Dict[str, float]] = None) -> Tuple[float, str]:
    base_risk = CLASS_RISK_BASE.get(predicted_class, 0.5)
    uncertainty_component = (1 - confidence) * 0.5
    class_component = base_risk * 0.5
    
    entropy_component = 0.0
    if probs:
        prob_array = np.array(list(probs.values()))
        entropy = compute_entropy(prob_array)
        entropy_component = min(entropy / 2.5, 1.0) * 0.1
    
    risk_score = np.clip(uncertainty_component + class_component + entropy_component, 0, 1)
    
    if risk_score < 0.25:
        risk_level = "LOW"
    elif risk_score < 0.5:
        risk_level = "MODERATE"
    elif risk_score < 0.75:
        risk_level = "HIGH"
    else:
        risk_level = "CRITICAL"
    
    return round(float(risk_score), 4), risk_level

# ==================== GRAD-CAM ====================
class GradCAM:
    def __init__(self, model: nn.Module, target_layer: str = "features"):
        self.model = model
        self.gradients = None
        self.activations = None
        self.hooks = []
        self.target_layer = target_layer
        self._register_hooks()
    
    def _register_hooks(self):
        def forward_hook(module, input, output):
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            self.gradients = grad_output[0].detach()
        
        try:
            target_module = dict(self.model.named_modules())[self.target_layer]
            self.hooks.append(target_module.register_forward_hook(forward_hook))
            self.hooks.append(target_module.register_full_backward_hook(backward_hook))
        except Exception as e:
            logger.warning(f"Grad-CAM hooks failed: {e}")
    
    def remove_hooks(self):
        for hook in self.hooks:
            hook.remove()
        self.hooks.clear()
    
    def generate(self, input_tensor: torch.Tensor, target_class: int) -> np.ndarray:
        if self.gradients is None or self.activations is None:
            return np.zeros((IMAGE_SIZE, IMAGE_SIZE))
        
        weights = torch.mean(self.gradients, dim=[2, 3], keepdim=True)
        cam = torch.sum(weights * self.activations, dim=1, keepdim=True)
        cam = F.relu(cam)
        cam = F.interpolate(cam, size=(IMAGE_SIZE, IMAGE_SIZE), mode='bilinear', align_corners=False)
        cam = cam.squeeze().cpu().numpy()
        
        if cam.max() != cam.min():
            cam = (cam - cam.min()) / (cam.max() - cam.min())
        return cam
    
    def overlay(self, image: np.ndarray, cam: np.ndarray, alpha: float = 0.5) -> np.ndarray:
        import cv2
        if cam.shape[:2] != image.shape[:2]:
            cam = cv2.resize(cam, (image.shape[1], image.shape[0]))
        
        heatmap = cv2.applyColorMap(np.uint8(255 * cam), cv2.COLORMAP_JET)
        heatmap = cv2.cvtColor(heatmap, cv2.COLOR_BGR2RGB)
        
        if image.dtype != np.uint8:
            image = (image * 255).astype(np.uint8)
        
        return cv2.addWeighted(image, 1 - alpha, heatmap, alpha, 0)

# ==================== INFERENCE ENGINE ====================
class WBCInferenceEngine:
    def __init__(self, model_path=None, device=None, num_classes=5,
                 enable_gradcam=True, class_names=None):
        self.model_path = Path(model_path) if model_path else DEFAULT_MODEL_PATH
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu') if device is None else torch.device(device)
        self.num_classes = num_classes
        self.enable_gradcam = enable_gradcam
        self.class_names = class_names or DEFAULT_WBC_CLASSES.copy()
        self.gradcam = None
        self.model = None
        self.model_info = None
        self.transform = self._build_transform()
        self._load_model()
    
    def _build_transform(self):
        return transforms.Compose([
            transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
            transforms.ToTensor(),
            transforms.Normalize(mean=MEAN, std=STD)
        ])
    
    def _load_model(self):
        try:
            # ← نفس البنية كالتدريب: efficientnet_v2_s مباشرة
            self.model = models.efficientnet_v2_s(weights=None)
            self.model.classifier[1] = nn.Linear(
                self.model.classifier[1].in_features, 
                self.num_classes
            )
            
            if self.model_path.exists():
                checkpoint = torch.load(self.model_path, map_location=self.device)
                
                if isinstance(checkpoint, dict):
                    if 'model_state_dict' in checkpoint:
                        state_dict = checkpoint['model_state_dict']
                    elif 'state_dict' in checkpoint:
                        state_dict = checkpoint['state_dict']
                    else:
                        state_dict = checkpoint
                else:
                    state_dict = checkpoint
                
                # ← تحميل الأوزان
                self.model.load_state_dict(state_dict, strict=False)
                logger.info("Model weights loaded")
                
                # ← التحقق
                with torch.no_grad():
                    dummy = torch.randn(1, 3, 224, 224)
                    out = self.model(dummy)
                    probs = F.softmax(out, dim=1)
                    max_prob = probs.max().item()
                    logger.info(f"Model test - Max confidence: {max_prob:.4f}")
                    
                    # إذا كان max_prob ~0.20، الأوزان لم تُحمَّل بشكل صحيح
                    if max_prob < 0.5:
                        logger.warning("Model confidence is low - weights may not be loaded correctly")
                
            else:
                logger.warning(f"Model file not found: {self.model_path}")
            
            self.model.to(self.device)
            self.model.eval()
            
            if self.enable_gradcam:
                try:
                    self.gradcam = GradCAM(self.model, target_layer="features")
                except Exception as e:
                    logger.warning(f"Grad-CAM failed: {e}")
                    self.gradcam = None
            
            self.model_info = ModelInfo(
                model_name=self.model_path.stem,
                architecture="efficientnet_v2_s",
                num_classes=self.num_classes,
                input_size=IMAGE_SIZE,
                device=str(self.device),
                gradcam_available=self.gradcam is not None,
                model_loaded=self.model_path.exists(),
                model_path=str(self.model_path),
                class_names=self.class_names
            )
            
        except Exception as e:
            logger.error(f"Model loading failed: {e}")
            self.model = None
            self.gradcam = None
            self.model_info = ModelInfo(
                model_name="ERROR",
                architecture="unknown",
                num_classes=self.num_classes,
                input_size=IMAGE_SIZE,
                device=str(self.device),
                gradcam_available=False,
                model_loaded=False,
                model_path=str(self.model_path),
                class_names=self.class_names
            )
    
    def get_model_info(self):
        if self.model_info:
            return asdict(self.model_info)
        return {
            "model_name": "NOT_LOADED",
            "architecture": "unknown",
            "num_classes": self.num_classes,
            "device": str(self.device),
            "gradcam_available": False,
            "model_loaded": False,
            "class_names": self.class_names
        }
    
    def preprocess(self, image):
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert('RGB')
        elif isinstance(image, np.ndarray):
            image = Image.fromarray(image).convert('RGB')
        
        tensor = self.transform(image)
        if tensor.dim() == 3:
            tensor = tensor.unsqueeze(0)
        return tensor.to(self.device)
    
    def predict(self, image, patient_id="P0000", image_name=None,
                return_gradcam=False, gradcam_output_path=None):
        start_time = datetime.now()
        
        if image_name is None:
            image_name = Path(image).name if isinstance(image, (str, Path)) else f"wbc_{start_time.strftime('%Y%m%d_%H%M%S')}.png"
        
        def error_result(msg):
            return InferenceResult(
                image_name=image_name,
                predicted_class="ERROR",
                confidence=0.0,
                probabilities={cls: 0.0 for cls in self.class_names},
                entropy=0.0,
                risk_score=1.0,
                risk_level="CRITICAL",
                inference_time_ms=0.0,
                device=str(self.device),
                timestamp=start_time,
                patient_id=patient_id,
                gradcam_available=False,
                error=msg
            )
        
        if self.model is None:
            return error_result("Model not loaded")
        
        try:
            input_tensor = self.preprocess(image)
            
            with torch.no_grad():
                outputs = self.model(input_tensor)
                probabilities = F.softmax(outputs, dim=1)
            
            probs_np = probabilities.cpu().numpy()[0]
            pred_idx = int(np.argmax(probs_np))
            pred_class = self.class_names[pred_idx] if pred_idx < len(self.class_names) else "Unknown"
            confidence = float(probs_np[pred_idx])
            
            prob_dict = {cls: float(probs_np[i]) if i < len(probs_np) else 0.0 
                        for i, cls in enumerate(self.class_names)}
            
            entropy = compute_entropy(probs_np)
            risk_score, risk_level = compute_risk_score(confidence, pred_class, prob_dict)
            
            gradcam_path = None
            gradcam_available = False
            
            if return_gradcam and gradcam_output_path:
                try:
                    gradcam_result = self._generate_gradcam(image, pred_idx, gradcam_output_path)
                    if gradcam_result:
                        gradcam_path = gradcam_output_path
                        gradcam_available = True
                except Exception as e:
                    logger.warning(f"Grad-CAM failed: {e}")
            
            inference_time_ms = (datetime.now() - start_time).total_seconds() * 1000
            
            return InferenceResult(
                image_name=image_name,
                predicted_class=pred_class,
                confidence=confidence,
                probabilities=prob_dict,
                entropy=entropy,
                risk_score=risk_score,
                risk_level=risk_level,
                inference_time_ms=round(inference_time_ms, 2),
                device=str(self.device),
                timestamp=start_time,
                patient_id=patient_id,
                gradcam_available=gradcam_available,
                gradcam_path=gradcam_path
            )
            
        except Exception as e:
            logger.error(f"Inference failed: {e}")
            return error_result(str(e))
    
    def _generate_gradcam(self, image, target_class=None, output_path=None):
        if self.model is None:
            return None
        
        if self.gradcam is None:
            try:
                self.gradcam = GradCAM(self.model, target_layer="features")
            except Exception as e:
                logger.warning(f"Grad-CAM init failed: {e}")
                return None
        
        self.gradcam.gradients = None
        self.gradcam.activations = None
        
        input_tensor = self.preprocess(image)
        input_tensor.requires_grad = True
        
        output = self.model(input_tensor)
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        self.model.zero_grad()
        output[0, target_class].backward()
        
        cam = self.gradcam.generate(input_tensor, target_class)
        
        if isinstance(image, (str, Path)):
            orig_img = np.array(Image.open(image).convert('RGB'))
        elif isinstance(image, Image.Image):
            orig_img = np.array(image.convert('RGB'))
        else:
            orig_img = image
        
        overlay = self.gradcam.overlay(orig_img, cam)
        
        if output_path:
            import cv2
            cv2.imwrite(output_path, cv2.cvtColor(overlay, cv2.COLOR_RGB2BGR))
            return output_path
        
        return overlay
    
    def predict_batch(self, images, patient_id="P0000", progress_callback=None):
        results = []
        for i, img in enumerate(images):
            img_name = Path(img).name if isinstance(img, (str, Path)) else f"batch_{i:04d}.png"
            result = self.predict(img, patient_id=patient_id, image_name=img_name)
            results.append(result)
            if progress_callback:
                progress_callback(i + 1, len(images))
        return results
    
    def __del__(self):
        try:
            if hasattr(self, "gradcam") and self.gradcam is not None:
                self.gradcam.remove_hooks()
        except Exception:
            pass

def load_engine(model_path=None, **kwargs):
    return WBCInferenceEngine(model_path=model_path, **kwargs)

if __name__ == "__main__":
    print("=" * 60)
    print("WBC Vision AI - Engine v7.0 Test")
    print("=" * 60)
    
    engine = WBCInferenceEngine()
    
    info = engine.get_model_info()
    print(f"\nModel Info:")
    for k, v in info.items():
        print(f"  {k}: {v}")
    
    dummy_img = np.random.randint(0, 255, (224, 224, 3), dtype=np.uint8)
    
    print(f"\nRunning inference on dummy image...")
    result = engine.predict(dummy_img, patient_id="TEST001")
    
    print(f"\nResult:")
    print(f"  Predicted: {result.predicted_class}")
    print(f"  Confidence: {result.confidence:.4f}")
    
    if result.error:
        print(f"  ⚠️ Error: {result.error}")
    else:
        print(f"  ✅ Success")
    
    print("\n" + "=" * 60)