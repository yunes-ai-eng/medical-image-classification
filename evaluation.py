"""
WBC Vision AI - Evaluation Engine
Pure evaluation logic only
No reporting, no exports, no UI dependencies
"""

import os
import torch
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime

from torchvision import datasets
from torch.utils.data import DataLoader, Subset
from sklearn.metrics import (
    accuracy_score, balanced_accuracy_score,
    precision_recall_fscore_support, confusion_matrix
)

from config import CLASS_NAMES, NUM_CLASSES


# ==================== DATA CLASS ====================

@dataclass
class EvaluationMetrics:
    """مقاييس التقييم النقية - لا تحتوي على منطق عرض"""
    accuracy: float
    balanced_accuracy: float
    precision: Dict[str, float]
    recall: Dict[str, float]
    f1_score: Dict[str, float]
    support: Dict[str, int]
    confusion_matrix: np.ndarray
    predictions: np.ndarray
    true_labels: np.ndarray
    probabilities: np.ndarray
    test_duration: float
    samples_count: int


# ==================== CORE EVALUATOR ====================

class WBCEvaluator:
    """
    مقيّم نقي - مسؤوليته الوحيدة:
    1. تشغيل inference على dataset
    2. حساب metrics
    
    لا يعرف شيئاً عن:
    - HTML reports
    - CSV exports
    - UI / Streamlit
    - File paths beyond data loading
    """
    
    def __init__(
        self,
        model: torch.nn.Module,
        device: torch.device,
        transform,
        num_workers: int = 0
    ):
        """
        Args:
            model: نموذج PyTorch جاهز (مُحمّل ومُجهّز مسبقاً)
            device: الجهاز (cuda/cpu)
            transform: تحويلات الصورة
            num_workers: عدد workers للـ DataLoader
        """
        self.model = model
        self.device = device
        self.transform = transform
        self.num_workers = num_workers
        
        # تأكيد أن النموذج في وضع التقييم
        self.model.eval()
        for param in self.model.parameters():
            param.requires_grad = False
    
    def evaluate(
        self,
        data_dir: str,
        batch_size: int = 32,
        num_samples: Optional[int] = None,
        random_seed: int = 42,
        collect_per_image: bool = False
    ) -> Tuple[EvaluationMetrics, Optional[List[Dict]]]:
        """
        تقييم النموذج على مجلد بيانات
        
        Args:
            data_dir: مسار البيانات (Test-A, Test-B, إلخ)
            batch_size: حجم الدفعة
            num_samples: عدد العينات (None = الكل)
            random_seed: بذرة عشوائية
            collect_per_image: هل نجمع بيانات لكل صورة؟
                             False = توفير ذاكرة للـ 5000+ صورة
        
        Returns:
            (metrics, per_image_results or None)
        """
        import time
        start_time = time.time()
        
        # ========== 1. تحميل البيانات ==========
        if not os.path.exists(data_dir):
            raise FileNotFoundError(f"Directory not found: {data_dir}")
        
        dataset = datasets.ImageFolder(data_dir, transform=self.transform)
        total = len(dataset)
        print(f"📁 Found {total} images in {data_dir}")
        
        # عينة عشوائية
        if num_samples and num_samples < total:
            np.random.seed(random_seed)
            indices = np.random.choice(total, num_samples, replace=False)
            dataset = Subset(dataset, indices)
            print(f"🎲 Selected {num_samples} images")
        
        # ========== 2. DataLoader ==========
        loader = DataLoader(
            dataset,
            batch_size=batch_size,
            shuffle=False,
            num_workers=self.num_workers,
            pin_memory=(self.device.type == "cuda")
        )
        
        # ========== 3. Inference Loop ==========
        all_preds, all_labels, all_probs = [], [], []
        per_image = [] if collect_per_image else None
        
        with torch.no_grad():
            for batch_idx, (imgs, labels) in enumerate(loader):
                imgs = imgs.to(self.device, non_blocking=True)
                
                # Mixed Precision
                device_type = "cuda" if self.device.type == "cuda" else "cpu"
                with torch.amp.autocast(device_type=device_type):
                    outputs = self.model(imgs)
                    probs = torch.softmax(outputs, dim=1)
                    preds = outputs.argmax(1)
                
                # نقل إلى CPU فوراً لتوفير VRAM
                preds_cpu = preds.cpu().numpy()
                probs_cpu = probs.cpu().numpy()
                labels_cpu = labels.numpy()
                
                all_preds.extend(preds_cpu)
                all_labels.extend(labels_cpu)
                all_probs.extend(probs_cpu)
                
                # جمع بيانات لكل صورة (اختياري)
                if collect_per_image:
                    for i in range(len(preds_cpu)):
                        per_image.append({
                            "index": len(all_preds) - len(preds_cpu) + i,
                            "true_class": CLASS_NAMES[labels_cpu[i]],
                            "predicted_class": CLASS_NAMES[preds_cpu[i]],
                            "correct": labels_cpu[i] == preds_cpu[i],
                            "confidence": float(probs_cpu[i][preds_cpu[i]])
                        })
                
                # تقدم
                if (batch_idx + 1) % 10 == 0:
                    processed = min((batch_idx + 1) * batch_size, len(dataset))
                    print(f"  Progress: {processed}/{len(dataset)}")
        
        # ========== 4. حساب المقاييس ==========
        all_preds = np.array(all_preds)
        all_labels = np.array(all_labels)
        all_probs = np.array(all_probs)
        
        metrics = self._compute_metrics(all_preds, all_labels, all_probs, start_time)
        
        print(f"✅ Done in {metrics.test_duration:.2f}s | Accuracy: {metrics.accuracy:.4f}")
        
        return metrics, per_image
    
    def _compute_metrics(
        self,
        predictions: np.ndarray,
        true_labels: np.ndarray,
        probabilities: np.ndarray,
        start_time: float
    ) -> EvaluationMetrics:
        """حساب المقاييس من النتائج"""
        
        precision, recall, f1, support = precision_recall_fscore_support(
            true_labels, predictions,
            average=None,
            labels=range(NUM_CLASSES),
            zero_division=0
        )
        
        return EvaluationMetrics(
            accuracy=accuracy_score(true_labels, predictions),
            balanced_accuracy=balanced_accuracy_score(true_labels, predictions),
            precision={CLASS_NAMES[i]: float(precision[i]) for i in range(NUM_CLASSES)},
            recall={CLASS_NAMES[i]: float(recall[i]) for i in range(NUM_CLASSES)},
            f1_score={CLASS_NAMES[i]: float(f1[i]) for i in range(NUM_CLASSES)},
            support={CLASS_NAMES[i]: int(support[i]) for i in range(NUM_CLASSES)},
            confusion_matrix=confusion_matrix(true_labels, predictions, labels=range(NUM_CLASSES)),
            predictions=predictions,
            true_labels=true_labels,
            probabilities=probabilities,
            test_duration=datetime.now().timestamp() - start_time,
            samples_count=len(predictions)
        )
    
    def evaluate_single(self, image) -> Dict:
        """
        تقييم صورة واحدة (للـ API / UI)
        """
        from PIL import Image
        
        if isinstance(image, (str, Path)):
            image = Image.open(image).convert("RGB")
        
        tensor = self.transform(image).unsqueeze(0).to(self.device)
        
        with torch.no_grad():
            device_type = "cuda" if self.device.type == "cuda" else "cpu"
            with torch.amp.autocast(device_type=device_type):
                output = self.model(tensor)
                probs = torch.softmax(output, dim=1)[0]
        
        pred_idx = int(probs.argmax())
        
        return {
            "predicted_class": CLASS_NAMES[pred_idx],
            "confidence": float(probs.max()),
            "probabilities": {CLASS_NAMES[i]: float(probs[i]) for i in range(NUM_CLASSES)}
        }


# ==================== STANDALONE TEST ====================

def quick_test(data_dir: str, model_path: str = "models/best_wbc_ultimate.pth", num_samples: int = 1000):
    """اختبار سريع من سطر الأوامر"""
    from engine import WBCInferenceEngine
    
    print("=" * 60)
    print("🔬 WBC Vision AI - Quick Test")
    print("=" * 60)
    
    # تحميل النموذج
    engine = WBCInferenceEngine()
    
    # إنشاء المقيّم
    evaluator = WBCEvaluator(
        model=engine.model,
        device=engine.device,
        transform=engine.transform,
        num_workers=0
    )
    
    # تقييم
    metrics, per_image = evaluator.evaluate(
        data_dir=data_dir,
        num_samples=num_samples,
        collect_per_image=True
    )
    
    # طباعة النتائج
    print("\n" + "=" * 60)
    print("📊 RESULTS")
    print("=" * 60)
    print(f"Accuracy: {metrics.accuracy:.4f}")
    print(f"Balanced Accuracy: {metrics.balanced_accuracy:.4f}")
    print(f"Duration: {metrics.test_duration:.2f}s")
    
    print("\nPer-Class Metrics:")
    for cls in CLASS_NAMES:
        print(f"  {cls:12} | P: {metrics.precision[cls]:.4f} | "
              f"R: {metrics.recall[cls]:.4f} | F1: {metrics.f1_score[cls]:.4f}")
    
    return metrics, per_image


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="WBC Model Evaluation")
    parser.add_argument("--data", required=True, help="Test data directory")
    parser.add_argument("--model", default="models/best_wbc_ultimate.pth", help="Model path")
    parser.add_argument("--samples", type=int, default=1000, help="Number of samples")
    parser.add_argument("--batch", type=int, default=32, help="Batch size")
    parser.add_argument("--workers", type=int, default=0, help="DataLoader workers")
    
    args = parser.parse_args()
    
    quick_test(args.data, args.model, args.samples)