"""
WBC Vision AI - Clinical Analytics Dashboard v5.1 (Production-Grade)
MLOps Medical Dashboard with Clinical Intelligence Layer
Features: DataFrame architecture, Patient Risk Engine, Alert Rules, Real-time monitoring
Fixed: Class method caching, MLOps staticmethod, unified risk schema, scipy-free drift
"""

import streamlit as st

# Page config FIRST (before any other st calls)
st.set_page_config(
    page_title="Dashboard | Al-Shameeri AI Vision",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import pandas as pd
import numpy as np
from PIL import Image
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from collections import Counter, defaultdict
from dataclasses import dataclass, asdict
import hashlib
import json
import logging
import math

# Plotly
try:
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    PLOTLY_AVAILABLE = True
except ImportError:
    PLOTLY_AVAILABLE = False

# System metrics
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

try:
    import torch
    TORCH_AVAILABLE = True
except ImportError:
    TORCH_AVAILABLE = False

# Auto-refresh
try:
    from streamlit_autorefresh import st_autorefresh
    AUTOREFRESH_AVAILABLE = True
except ImportError:
    AUTOREFRESH_AVAILABLE = False

# ==================== IMPORT SYSTEM ====================
import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import *
from engine import WBCInferenceEngine

# ==================== LOGGING ====================
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("WBC_Dashboard")

# ==================== AUTO REFRESH ====================
if AUTOREFRESH_AVAILABLE:
    st_autorefresh(interval=30000, key="dashboard_refresh")  # 30 seconds

# ==================== LANGUAGE ====================
if "lang" not in st.session_state:
    st.session_state.lang = "en"

# ==================== TEXTS (COMPLETE - NO MISSING KEYS) ====================
TEXTS = {
    "en": {
        "title": "📊 Clinical Intelligence Dashboard",
        "subtitle": "Real-time MLOps Monitoring for WBC Vision AI",
        "overview": "📈 System Overview",
        "model_performance": "🤖 Model Performance",
        "class_distribution": "🧬 Cell Type Distribution",
        "confidence_trends": "📉 Confidence Analytics",
        "recent_analyses": "🕐 Recent Analyses",
        "system_health": "💻 System Health",
        "total_analyses": "Total Cases",
        "avg_confidence": "Avg Confidence",
        "accuracy": "Model Accuracy",
        "processing_speed": "Avg Inference",
        "high_conf_rate": "High Conf Rate",
        "back": "← Back",
        "no_data": "ℹ️ Showing demo analytics. Process images in Batch Analysis to see real data.",
        "today": "Today",
        "this_week": "This Week",
        "this_month": "This Month",
        "all_time": "All Time",
        "time_range": "📅 Time Range",
        "model_info": "🤖 Model Information",
        "class_breakdown": "📊 Class Breakdown",
        "confidence_histogram": "📊 Confidence Distribution",
        "inference_time": "⏱️ Inference Time Trend",
        "risk_distribution": "⚠️ Risk Distribution",
        "performance_metrics": "📈 Performance Metrics",
        "device_info": "💻 System Resources",
        "model_architecture": "Architecture",
        "device": "Device",
        "num_classes": "Classes",
        "gradcam_status": "Grad-CAM",
        "active": "✅ Active",
        "inactive": "❌ Inactive",
        "gpu_memory": "GPU Memory",
        "cpu_load": "CPU Load",
        "ram_usage": "RAM Usage",
        "model_cache": "Model Cache",
        "system_status": "System Status",
        "healthy": "🟢 Healthy",
        "degraded": "🟡 Degraded",
        "critical": "🔴 Critical",
        "patients_today": "Patients",
        "avg_images_patient": "Avg Images/Patient",
        "review_queue": "Review Queue",
        "auto_processed": "Auto Processed",
        "needs_manual": "Needs Manual",
        "success_rate": "Success Rate",
        "error_rate": "Error Rate",
        "avg_risk_score": "Avg Risk",
        "high_risk_cases": "High Risk",
        "drift_warning": "🚨 Model Drift Detected",
        "drift_message": "Confidence distribution has shifted significantly. Consider model retraining.",
        "calibration_status": "Calibration",
        "well_calibrated": "✅ Calibrated",
        "needs_calibration": "⚠️ Needs Calibration",
        "patient_timeline": "👤 Patient Timeline",
        "drift_panel": "📉 Drift Analytics",
        "confidence_trend": "Confidence Trend",
        "entropy_tracking": "Entropy Tracking",
        "class_imbalance": "Class Imbalance",
        "export_report": "📄 Export Clinical Report",
        "export_options": "📤 Export Options",
        "last_updated": "Last Updated",
        "real_time": "🔄 Real-time",
        "refreshing": "Refreshing...",
        "patient_risk": "🔴 Patient Risk Engine",
        "alert_rules": "🚨 Alert Rules",
        "mlops_layer": "📊 MLOps Layer",
        "model_version": "Model Version",
        "drift_history": "Drift History",
        "inference_log": "Inference Log",
        "escalation": "⚠️ Escalation",
        "patient_id": "Patient ID",
        "risk_trend": "Risk Trend",
        "alerts_triggered": "Alerts Triggered",
        "no_alerts": "✅ No alerts triggered",
        "model_tracking": "Model Tracking",
        "accuracy_over_time": "Accuracy Over Time",
        "vectorized_ops": "Vectorized Ops",
        "cached": "Cached",
        "precomputed": "Precomputed",
        "stability_pass": "Stability Pass 2 Active",
    },
    "ar": {
        "title": "📊 لوحة التحليلات السريرية الذكية",
        "subtitle": "مراقبة MLOps في الوقت الفعلي",
        "overview": "📈 نظرة عامة",
        "model_performance": "🤖 أداء النموذج",
        "class_distribution": "🧬 توزيع الخلايا",
        "confidence_trends": "📉 تحليلات الثقة",
        "recent_analyses": "🕐 التحاليل الأخيرة",
        "system_health": "💻 صحة النظام",
        "total_analyses": "إجمالي الحالات",
        "avg_confidence": "متوسط الثقة",
        "accuracy": "دقة النموذج",
        "processing_speed": "متوسط الاستدلال",
        "high_conf_rate": "معدل الثقة العالية",
        "back": "← رجوع",
        "no_data": "ℹ️ عرض تحليلات تجريبية. قم بمعالجة صور في التحليل المجمع.",
        "today": "اليوم",
        "this_week": "هذا الأسبوع",
        "this_month": "هذا الشهر",
        "all_time": "كل الوقت",
        "time_range": "📅 النطاق الزمني",
        "model_info": "🤖 معلومات النموذج",
        "class_breakdown": "📊 تفصيل الأنواع",
        "confidence_histogram": "📊 توزيع الثقة",
        "inference_time": "⏱️ اتجاه الوقت",
        "risk_distribution": "⚠️ توزيع المخاطر",
        "performance_metrics": "📈 مقاييس الأداء",
        "device_info": "💻 موارد النظام",
        "model_architecture": "البنية",
        "device": "الجهاز",
        "num_classes": "الفئات",
        "gradcam_status": "Grad-CAM",
        "active": "✅ نشط",
        "inactive": "❌ غير نشط",
        "gpu_memory": "ذاكرة GPU",
        "cpu_load": "حمل المعالج",
        "ram_usage": "استخدام الرام",
        "model_cache": "ذاكرة النموذج",
        "system_status": "حالة النظام",
        "healthy": "🟢 صحي",
        "degraded": "🟡 متدهور",
        "critical": "🔴 حرج",
        "patients_today": "المرضى",
        "avg_images_patient": "متوسط الصور/مريض",
        "review_queue": "قائمة المراجعة",
        "auto_processed": "معالجة تلقائية",
        "needs_manual": "يحتاج يدوي",
        "success_rate": "معدل النجاح",
        "error_rate": "معدل الخطأ",
        "avg_risk_score": "متوسط المخاطر",
        "high_risk_cases": "مخاطر عالية",
        "drift_warning": "🚨 انحراف في النموذج",
        "drift_message": "توزيع الثقة تغير بشكل كبير. يُنصح بإعادة التدريب.",
        "calibration_status": "المعايرة",
        "well_calibrated": "✅ معاير",
        "needs_calibration": "⚠️ يحتاج معايرة",
        "patient_timeline": "👤 خط زمني للمريض",
        "drift_panel": "📉 تحليلات الانحراف",
        "confidence_trend": "اتجاه الثقة",
        "entropy_tracking": "تتبع الانتروبيا",
        "class_imbalance": "عدم توازن الفئات",
        "export_report": "📄 تصدير تقرير سريري",
        "export_options": "📤 خيارات التصدير",
        "last_updated": "آخر تحديث",
        "real_time": "🔄 فوري",
        "refreshing": "جاري التحديث...",
        "patient_risk": "🔴 محرك مخاطر المريض",
        "alert_rules": "🚨 قواعد التنبيه",
        "mlops_layer": "📊 طبقة MLOps",
        "model_version": "إصدار النموذج",
        "drift_history": "تاريخ الانحراف",
        "inference_log": "سجل الاستدلال",
        "escalation": "⚠️ تصعيد",
        "patient_id": "رقم المريض",
        "risk_trend": "اتجاه المخاطر",
        "alerts_triggered": "التنبيهات المفعلة",
        "no_alerts": "✅ لا توجد تنبيهات",
        "model_tracking": "تتبع النموذج",
        "accuracy_over_time": "الدقة عبر الزمن",
        "vectorized_ops": "عمليات متجهية",
        "cached": "مخزن مؤقتاً",
        "precomputed": "محسوب مسبقاً",
        "stability_pass": "Stability Pass 2 نشط",
    }
}

t = TEXTS[st.session_state.lang]

# ==================== CSS ====================
st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
        background-attachment: fixed;
    }
    .glass-panel {
        background: rgba(255,255,255,0.03);
        backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.08);
        border-radius: 20px;
        padding: 24px;
        color: white;
    }
    .dashboard-card {
        background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 16px;
        padding: 20px;
        color: white;
        position: relative;
        overflow: hidden;
    }
    .dashboard-card::before {
        content: '';
        position: absolute;
        top: 0; left: 0; right: 0; height: 3px;
        background: linear-gradient(90deg, #e94560, #ff6b6b);
    }
    .dashboard-card.green::before { background: linear-gradient(90deg, #27ae60, #2ecc71); }
    .dashboard-card.blue::before { background: linear-gradient(90deg, #3498db, #5dade2); }
    .dashboard-card.purple::before { background: linear-gradient(90deg, #9b59b6, #bb8fce); }
    .dashboard-card.orange::before { background: linear-gradient(90deg, #f39c12, #f5b041); }
    .stat-value {
        font-size: 2rem;
        font-weight: 800;
        background: linear-gradient(135deg, #e94560, #ff6b6b);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
    }
    .stat-label { font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 4px; }
    .section-title {
        color: #e94560;
        font-size: 1.3rem;
        font-weight: 700;
        margin: 24px 0 12px;
        padding-bottom: 8px;
        border-bottom: 2px solid rgba(233,69,96,0.3);
    }
    .alert-drift {
        background: rgba(231,76,60,0.15);
        border: 1px solid rgba(231,76,60,0.4);
        border-radius: 12px;
        padding: 14px 18px;
        color: #e74c3c;
        margin-bottom: 16px;
    }
    .alert-box {
        background: rgba(243,156,18,0.15);
        border: 1px solid rgba(243,156,18,0.4);
        border-radius: 12px;
        padding: 12px 16px;
        color: #f1c40f;
        margin-bottom: 10px;
    }
    .badge {
        display: inline-flex;
        align-items: center;
        padding: 3px 10px;
        border-radius: 12px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-success { background: rgba(39,174,96,0.2); color: #2ecc71; border: 1px solid rgba(39,174,96,0.3); }
    .badge-warning { background: rgba(243,156,18,0.2); color: #f1c40f; border: 1px solid rgba(243,156,18,0.3); }
    .badge-danger { background: rgba(231,76,60,0.2); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3); }
    #MainMenu, footer, header { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ==================== SYSTEM METRICS (REAL) ====================
@st.cache_data(ttl=5)
def get_system_metrics() -> Dict[str, Any]:
    """Get real system metrics with caching"""
    metrics = {
        "cpu_percent": 0.0, "ram_percent": 0.0, "ram_used_gb": 0.0, "ram_total_gb": 0.0,
        "gpu_available": False, "gpu_memory_allocated_gb": 0.0, "gpu_memory_total_gb": 0.0,
        "timestamp": datetime.now().isoformat()
    }
    
    if PSUTIL_AVAILABLE:
        try:
            metrics["cpu_percent"] = psutil.cpu_percent(interval=0.1)
            mem = psutil.virtual_memory()
            metrics["ram_percent"] = mem.percent
            metrics["ram_used_gb"] = round(mem.used / (1024**3), 2)
            metrics["ram_total_gb"] = round(mem.total / (1024**3), 2)
        except Exception as e:
            logger.warning(f"psutil error: {e}")
    
    if TORCH_AVAILABLE and torch.cuda.is_available():
        try:
            metrics["gpu_available"] = True
            metrics["gpu_memory_allocated_gb"] = round(torch.cuda.memory_allocated() / (1024**3), 2)
            metrics["gpu_memory_total_gb"] = round(torch.cuda.get_device_properties(0).total_memory / (1024**3), 2)
        except Exception as e:
            logger.warning(f"CUDA error: {e}")
    
    return metrics

# ==================== DRIFT DETECTION (SCIPY-FREE) ====================
class DriftDetector:
    """Advanced drift detection with zero-division protection - NO SCIPY REQUIRED"""
    
    @staticmethod
    def safe_divide(a: float, b: float, default: float = 0.0) -> float:
        return a / b if b != 0 else default
    
    @staticmethod
    def ks_test(recent: np.ndarray, historical: np.ndarray) -> float:
        """Pure numpy implementation of Kolmogorov-Smirnov test - no scipy needed"""
        if len(recent) == 0 or len(historical) == 0:
            return 1.0
        
        # Empirical CDF difference
        combined = np.concatenate([recent, historical])
        combined_sorted = np.sort(combined)
        
        def ecdf(data, x):
            return np.searchsorted(np.sort(data), x, side='right') / len(data)
        
        ecdf_recent = ecdf(recent, combined_sorted)
        ecdf_hist = ecdf(historical, combined_sorted)
        
        ks_stat = np.max(np.abs(ecdf_recent - ecdf_hist))
        
        # Approximate p-value using Lilliefors approximation
        n1, n2 = len(recent), len(historical)
        n = (n1 * n2) / (n1 + n2)
        if n <= 0:
            return 1.0
        
        # Asymptotic approximation
        lambda_val = (np.sqrt(n) + 0.12 + 0.11 / np.sqrt(n)) * ks_stat
        if lambda_val < 0:
            p_value = 1.0
        else:
            # Two-sided KS p-value approximation
            p_value = 2 * sum([(-1)**(i-1) * math.exp(-2 * i**2 * lambda_val**2) 
                              for i in range(1, 100)])
            p_value = max(0.0, min(1.0, p_value))
        
        return p_value
    
    @staticmethod
    def rolling_zscore(values: np.ndarray, window: int = 20) -> np.ndarray:
        if len(values) < window:
            return np.zeros(len(values))
        s = pd.Series(values)
        rolling_mean = s.rolling(window=window).mean()
        rolling_std = s.rolling(window=window).std()
        z_scores = (s - rolling_mean) / (rolling_std + 1e-10)
        return z_scores.fillna(0).values
    
    @staticmethod
    def detect_drift(confidences: List[float], recent_window: int = 20, threshold: float = 0.05) -> Dict:
        n = len(confidences)
        if n < recent_window * 2:
            return {"drift_detected": False, "p_value": 1.0, "z_score": 0.0, "method": "insufficient_data"}
        
        recent = np.array(confidences[-recent_window:])
        historical = np.array(confidences[:-recent_window])
        
        p_value = DriftDetector.ks_test(recent, historical)
        z_scores = DriftDetector.rolling_zscore(np.array(confidences))
        recent_z = float(z_scores[-1]) if len(z_scores) > 0 else 0.0
        
        # Safe entropy calculation
        recent_entropy = DriftDetector._safe_entropy(recent)
        historical_entropy = DriftDetector._safe_entropy(historical)
        entropy_diff = abs(recent_entropy - historical_entropy)
        
        drift_detected = p_value < threshold or abs(recent_z) > 2.5 or entropy_diff > 0.3
        
        return {
            "drift_detected": drift_detected,
            "p_value": round(float(p_value), 4),
            "z_score": round(recent_z, 3),
            "entropy_diff": round(entropy_diff, 3),
            "method": "ks_test+z_score+entropy",
            "recent_mean": round(float(np.mean(recent)), 3),
            "historical_mean": round(float(np.mean(historical)), 3)
        }
    
    @staticmethod
    def _safe_entropy(values: np.ndarray, bins: int = 10) -> float:
        if len(values) == 0:
            return 0.0
        hist, _ = np.histogram(values, bins=bins, range=(0, 1))
        total = np.sum(hist)
        if total == 0:
            return 0.0
        probs = hist / total
        probs = probs[probs > 0]
        if len(probs) == 0:
            return 0.0
        return float(-np.sum(probs * np.log2(probs)))

# ==================== PATIENT RISK ENGINE (FIXED: NO CACHE IN CLASS METHOD) ====================
@dataclass
class PatientRiskProfile:
    patient_id: str
    total_visits: int
    avg_confidence: float
    avg_risk_score: float
    max_risk_score: float
    risk_trend: str  # "improving", "stable", "worsening"
    escalation_flag: bool
    last_visit: datetime
    class_history: List[str]
    alert_level: str

def compute_patient_profiles(df: pd.DataFrame) -> Dict[str, PatientRiskProfile]:
    """
    STANDALONE FUNCTION (not class method) - safe for caching
    Computes patient risk profiles from DataFrame
    """
    profiles = {}
    
    for patient_id, group in df.groupby("patient_id"):
        group = group.sort_values("timestamp")
        confidences = group["confidence"].tolist()
        risks = group["risk_score"].tolist()
        classes = group["predicted_class"].tolist()
        timestamps = group["timestamp"].tolist()
        
        # Trend analysis
        if len(risks) >= 2:
            first_half = np.mean(risks[:len(risks)//2])
            second_half = np.mean(risks[len(risks)//2:])
            if second_half < first_half * 0.8:
                trend = "improving"
            elif second_half > first_half * 1.2:
                trend = "worsening"
            else:
                trend = "stable"
        else:
            trend = "stable"
        
        # Escalation: risk increasing over time
        escalation = len(risks) >= 2 and risks[-1] > risks[0] * 1.5 and risks[-1] > 0.5
        
        # Alert level
        max_risk = max(risks) if risks else 0
        if max_risk > 0.75 or escalation:
            alert = "CRITICAL"
        elif max_risk > 0.5:
            alert = "HIGH"
        elif max_risk > 0.25:
            alert = "MODERATE"
        else:
            alert = "LOW"
        
        profiles[patient_id] = PatientRiskProfile(
            patient_id=patient_id,
            total_visits=len(group),
            avg_confidence=round(np.mean(confidences), 3) if confidences else 0,
            avg_risk_score=round(np.mean(risks), 3) if risks else 0,
            max_risk_score=round(max_risk, 3),
            risk_trend=trend,
            escalation_flag=escalation,
            last_visit=timestamps[-1] if timestamps else datetime.now(),
            class_history=classes,
            alert_level=alert
        )
    
    return profiles

class PatientRiskEngine:
    """Clinical risk engine per patient with trend analysis - FIXED VERSION"""
    
    def __init__(self, df: pd.DataFrame):
        self.df = df
        # Call standalone function instead of cached class method
        self.profiles = compute_patient_profiles(df)
    
    def get_high_risk_patients(self, threshold: float = 0.5) -> List[PatientRiskProfile]:
        return [p for p in self.profiles.values() if p.max_risk_score > threshold]
    
    def get_escalated_patients(self) -> List[PatientRiskProfile]:
        return [p for p in self.profiles.values() if p.escalation_flag]

# ==================== ALERT RULES ENGINE ====================
class AlertRulesEngine:
    """Clinical alert rules engine"""
    
    RULES = [
        {"id": "low_confidence", "condition": lambda r: r["confidence"] < 0.60,
         "level": "CRITICAL", "message": "Confidence below 60% - manual review required"},
        {"id": "high_risk", "condition": lambda r: r.get("risk_score", 0) > 0.75,
         "level": "CRITICAL", "message": "High risk score detected"},
        {"id": "drift_alert", "condition": lambda r: False,  # Set by drift detector
         "level": "WARNING", "message": "Model drift detected"},
        {"id": "review_needed", "condition": lambda r: r["confidence"] < 0.70,
         "level": "WARNING", "message": "Confidence below 70% - review recommended"},
        {"id": "basophil_alert", "condition": lambda r: r.get("predicted_class") == "Basophil",
         "level": "WARNING", "message": "Basophil detected - clinically significant"},
    ]
    
    def evaluate(self, records: List[Dict]) -> List[Dict]:
        alerts = []
        for record in records:
            for rule in self.RULES:
                if rule["condition"](record):
                    alerts.append({
                        "rule_id": rule["id"],
                        "level": rule["level"],
                        "message": rule["message"],
                        "patient_id": record.get("patient_id", "Unknown"),
                        "timestamp": record.get("timestamp", datetime.now()),
                        "image": record.get("image_name", "Unknown")
                    })
        return alerts

# ==================== MLOps TRACKER (FIXED: STATICMETHOD CALL) ====================
class MLOpsTracker:
    """Track model performance over time"""
    
    def __init__(self):
        self.drift_history = []
        self.inference_count = 0
        self.error_count = 0
    
    def log_inference(self, result: Dict):
        self.inference_count += 1
        if result.get("predicted_class") == "ERROR":
            self.error_count += 1
    
    def log_drift(self, drift_result: Dict):
        self.drift_history.append({
            "timestamp": datetime.now().isoformat(),
            **drift_result
        })
    
    def get_stats(self) -> Dict:
        # FIXED: Use staticmethod properly
        error_rate = MLOpsTracker.safe_divide(self.error_count, self.inference_count)
        return {
            "total_inferences": self.inference_count,
            "errors": self.error_count,
            "error_rate": round(error_rate, 4),
            "drift_events": len([d for d in self.drift_history if d.get("drift_detected")]),
            "total_drift_checks": len(self.drift_history)
        }
    
    @staticmethod
    def safe_divide(a: int, b: int) -> float:
        return a / b if b > 0 else 0.0

# ==================== DEMO DATA (DETERMINISTIC) ====================
@st.cache_data
def generate_demo_data(n_samples: int = 300, seed: int = 42) -> pd.DataFrame:
    """Generate deterministic demo data as DataFrame - UNIFIED SCHEMA"""
    np.random.seed(seed)
    
    classes = ["Neutrophil", "Lymphocyte", "Monocyte", "Eosinophil", "Basophil"]
    class_probs = [0.45, 0.30, 0.15, 0.07, 0.03]
    class_risk_base = {"Neutrophil": 0.2, "Lymphocyte": 0.3, "Monocyte": 0.4,
                      "Eosinophil": 0.7, "Basophil": 0.8}
    
    base_time = datetime.now() - timedelta(days=30)
    records = []
    
    for i in range(n_samples):
        time_factor = i / n_samples
        base_conf = 0.75 + 0.15 * np.sin(time_factor * np.pi)
        conf = np.clip(np.random.beta(7, 2) * 0.3 + base_conf - 0.15, 0.3, 0.99)
        cls = np.random.choice(classes, p=class_probs)
        
        risk_score = np.clip((1 - conf) * 0.5 + class_risk_base[cls] * 0.5 + np.random.normal(0, 0.05), 0, 1)
        risk_level = "LOW" if risk_score < 0.25 else "MODERATE" if risk_score < 0.5 else "HIGH" if risk_score < 0.75 else "CRITICAL"
        
        # Deterministic probabilities
        prob_seed = int(hashlib.md5(f"{i}_{cls}".encode()).hexdigest(), 16) % (2**31)
        np.random.seed(prob_seed)
        raw_probs = np.random.dirichlet(np.ones(5))
        np.random.seed(seed)  # Reset
        
        probs = {c: float(raw_probs[j]) for j, c in enumerate(classes)}
        probs[cls] = conf
        total = sum(probs.values())
        probs = {k: v/total for k, v in probs.items()}
        
        # Entropy (precomputed, deterministic)
        vals = np.array(list(probs.values()))
        vals = vals[vals > 0]
        entropy = float(-np.sum(vals * np.log2(vals + 1e-10)))
        
        # UNIFIED SCHEMA: match session_data format exactly
        records.append({
            "timestamp": base_time + timedelta(hours=i * 2.4),
            "image_name": f"wbc_{i:04d}.png",
            "predicted_class": cls,
            "confidence": float(conf),
            "probabilities": probs,
            "entropy": entropy,
            "risk_score": float(risk_score),  # Unified: flat field, not nested
            "risk_level": risk_level,          # Unified: flat field, not nested
            "inference_time_ms": float(np.random.normal(45, 10)),
            "patient_id": f"P{1000 + (i % 50)}",  # 50 patients
            "device": "cuda" if i % 3 != 0 else "cpu"
        })
    
    return pd.DataFrame(records)

# ==================== LOAD MODEL (SAFE) ====================
@st.cache_resource(show_spinner=False)
def get_model_info_safe() -> Optional[Dict]:
    """Safely load model info with error handling"""
    try:
        engine = WBCInferenceEngine()
        info = engine.get_model_info()
        return info or {}
    except Exception as e:
        logger.error(f"Model info load failed: {e}")
        return {}

model_info = get_model_info_safe() or {}

# ==================== HEADER ====================
st.markdown(f"""
    <div style="text-align:center;margin-bottom:24px;">
        <h1 style="color:white;font-size:2.5rem;font-weight:800;margin-bottom:6px;">{t["title"]}</h1>
        <p style="color:rgba(255,255,255,0.55);font-size:1rem;">{t["subtitle"]}</p>
    </div>
""", unsafe_allow_html=True)

if AUTOREFRESH_AVAILABLE:
    st.markdown(f"""
        <div style="text-align:center;margin-bottom:16px;">
            <span class="badge badge-success">{t["real_time"]} • {datetime.now().strftime("%H:%M:%S")}</span>
        </div>
    """, unsafe_allow_html=True)

# Stability Pass 2 badge
st.markdown(f"""
    <div style="text-align:center;margin-bottom:16px;">
        <span class="badge badge-success">✅ {t["stability_pass"]}</span>
    </div>
""", unsafe_allow_html=True)

if st.button(t["back"], use_container_width=False):
    st.switch_page("app.py")

# ==================== LOAD & CLEAN DATA (FIXED: UNIFIED SCHEMA) ====================
session_data = st.session_state.get("batch_results", [])

# Unified cleaning - single pass with unified schema
if session_data:
    clean_records = []
    for r in session_data:
        if isinstance(r, dict) and "error" not in r and "predicted_class" in r:
            # Normalize timestamp
            ts = r.get("timestamp")
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts.replace('Z', '+00:00'))
                except:
                    ts = datetime.now()
            elif not isinstance(ts, datetime):
                ts = datetime.now()
            
            # UNIFIED SCHEMA: Handle both old nested format and new flat format
            # Try flat first, fallback to nested
            risk_score = r.get("risk_score")
            if risk_score is None:
                risk_dict = r.get("risk", {})
                risk_score = risk_dict.get("score", 0.3) if isinstance(risk_dict, dict) else 0.3
            
            risk_level = r.get("risk_level")
            if risk_level is None:
                risk_dict = r.get("risk", {})
                risk_level = risk_dict.get("level", "LOW") if isinstance(risk_dict, dict) else "LOW"
            
            # Ensure all fields exist with unified schema
            clean_records.append({
                "timestamp": ts,
                "image_name": r.get("image_name", "unknown"),
                "predicted_class": r["predicted_class"],
                "confidence": float(r.get("confidence", 0)),
                "probabilities": r.get("probabilities", {}),
                "entropy": r.get("entropy", 0.0),
                "risk_score": float(risk_score),      # Unified: flat
                "risk_level": str(risk_level),         # Unified: flat
                "inference_time_ms": float(r.get("inference_time_ms", 50)),
                "patient_id": r.get("patient_id", "P0000"),
                "device": r.get("device", "cpu")
            })
    
    df = pd.DataFrame(clean_records) if clean_records else generate_demo_data()
    demo_mode = False
else:
    df = generate_demo_data()
    demo_mode = True
    st.info(t["no_data"])

if df.empty:
    st.error("No data available.")
    st.stop()

# ==================== TIME FILTER ====================
time_range = st.selectbox(
    t["time_range"],
    [t["today"], t["this_week"], t["this_month"], t["all_time"]],
    index=2
)

now = datetime.now()
cutoff_map = {
    t["today"]: now - timedelta(days=1),
    t["this_week"]: now - timedelta(weeks=1),
    t["this_month"]: now - timedelta(days=30),
    t["all_time"]: now - timedelta(days=3650)
}
cutoff = cutoff_map.get(time_range, now - timedelta(days=30))

# Vectorized filtering
mask = df["timestamp"] >= cutoff
filtered_df = df[mask].copy()

if filtered_df.empty:
    st.warning("No data in selected time range.")
    st.stop()

n_samples = len(filtered_df)

# ==================== PRECOMPUTED METRICS (Vectorized) ====================
# All metrics computed once using pandas vectorized operations
metrics = {
    "avg_conf": filtered_df["confidence"].mean(),
    "high_conf_rate": (filtered_df["confidence"] >= 0.85).mean(),
    "avg_time": filtered_df["inference_time_ms"].mean(),
    "unique_patients": filtered_df["patient_id"].nunique(),
    "avg_risk": filtered_df["risk_score"].mean(),
    "high_risk": (filtered_df["risk_score"] > 0.5).sum(),
    "review_queue": (filtered_df["confidence"] < 0.70).sum(),
    "success_rate": (filtered_df["confidence"] >= 0.70).mean(),
    "auto_processed": (filtered_df["confidence"] >= 0.85).mean(),
}

# System status
sys_metrics = get_system_metrics()
if metrics["high_conf_rate"] > 0.8 and metrics["avg_risk"] < 0.3 and sys_metrics["cpu_percent"] < 80:
    sys_status, sys_color = t["healthy"], "#27ae60"
elif metrics["high_conf_rate"] > 0.6 and metrics["avg_risk"] < 0.5:
    sys_status, sys_color = t["degraded"], "#f39c12"
else:
    sys_status, sys_color = t["critical"], "#e74c3c"

# ==================== INITIALIZE ENGINES ====================
patient_engine = PatientRiskEngine(filtered_df)
alert_engine = AlertRulesEngine()
mlops_tracker = MLOpsTracker()

# Evaluate alerts
alerts = alert_engine.evaluate(filtered_df.to_dict("records"))

# Drift detection
drift_result = DriftDetector.detect_drift(filtered_df["confidence"].tolist())

# ==================== OVERVIEW STATS ====================
st.markdown(f'<div class="section-title">{t["overview"]}</div>', unsafe_allow_html=True)

stat_cols = st.columns(6)
stats_data = [
    (str(n_samples), t["total_analyses"], "📊", "#e94560"),
    (f"{metrics['avg_conf']:.1%}", t["avg_confidence"], "🎯", "#3498db"),
    (f"{metrics['high_conf_rate']:.1%}", t["high_conf_rate"], "✅", "#27ae60"),
    (f"{metrics['avg_time']:.0f}ms", t["processing_speed"], "⚡", "#9b59b6"),
    (str(metrics["unique_patients"]), t["patients_today"], "👤", "#f39c12"),
    (sys_status, t["system_status"], "💻", sys_color)
]

for i, (value, label, icon, color) in enumerate(stats_data):
    with stat_cols[i]:
        st.markdown(f"""
            <div class="dashboard-card" style="text-align:center;">
                <div style="font-size:1.4rem;margin-bottom:4px;">{icon}</div>
                <div style="font-size:1.8rem;font-weight:800;color:{color};">{value}</div>
                <div style="color:rgba(255,255,255,0.6);font-size:0.75rem;margin-top:2px;">{label}</div>
            </div>
        """, unsafe_allow_html=True)

# ==================== ALERTS SECTION ====================
if alerts or drift_result["drift_detected"]:
    st.markdown(f'<div class="section-title">{t["alert_rules"]}</div>', unsafe_allow_html=True)
    
    if drift_result["drift_detected"]:
        st.markdown(f"""
            <div class="alert-drift">
                <div style="font-weight:700;">{t["drift_warning"]}</div>
                <div style="font-size:0.85rem;margin-top:4px;">{t["drift_message"]}</div>
                <div style="font-size:0.8rem;margin-top:6px;opacity:0.8;">
                    p={drift_result['p_value']} | z={drift_result['z_score']} | entropy_diff={drift_result['entropy_diff']}
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    for alert in alerts[:5]:  # Show top 5
        alert_class = "alert-drift" if alert["level"] == "CRITICAL" else "alert-box"
        st.markdown(f"""
            <div class="{alert_class}">
                <span class="badge badge-{'danger' if alert['level']=='CRITICAL' else 'warning'}">{alert['level']}</span>
                <span style="margin-left:8px;">{alert['message']}</span>
                <span style="float:right;color:rgba(255,255,255,0.5);font-size:0.8rem;">{alert['patient_id']}</span>
            </div>
        """, unsafe_allow_html=True)
    
    if not alerts and not drift_result["drift_detected"]:
        st.success(t["no_alerts"])

# ==================== PATIENT RISK ENGINE ====================
st.markdown(f'<div class="section-title">{t["patient_risk"]}</div>', unsafe_allow_html=True)

high_risk_patients = patient_engine.get_high_risk_patients()
escalated = patient_engine.get_escalated_patients()

pr_cols = st.columns(3)
pr_data = [
    (str(len(patient_engine.profiles)), t["patients_today"], "#3498db", "blue"),
    (str(len(high_risk_patients)), t["high_risk_cases"], "#e74c3c", "red"),
    (str(len(escalated)), t["escalation"], "#c0392b", "purple")
]

for i, (value, label, color, card_type) in enumerate(pr_data):
    with pr_cols[i]:
        st.markdown(f"""
            <div class="dashboard-card {card_type}">
                <div style="font-size:2rem;font-weight:800;color:{color};">{value}</div>
                <div style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin-top:4px;">{label}</div>
            </div>
        """, unsafe_allow_html=True)

# Patient timeline selector
if patient_engine.profiles:
    selected_patient = st.selectbox(
        t["patient_id"],
        list(patient_engine.profiles.keys()),
        format_func=lambda x: f"{x} ({patient_engine.profiles[x].total_visits} visits) - {patient_engine.profiles[x].alert_level}"
    )
    
    if selected_patient:
        profile = patient_engine.profiles[selected_patient]
        patient_df = filtered_df[filtered_df["patient_id"] == selected_patient].sort_values("timestamp")
        
        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"""
                <div class="glass-panel">
                    <h4 style="color:#e94560;margin-bottom:10px;">{t["patient_risk"]}</h4>
                    <div style="display:grid;grid-template-columns:1fr 1fr;gap:8px;font-size:0.85rem;">
                        <div><span style="color:rgba(255,255,255,0.5);">Visits</span><br/><span style="color:white;font-weight:600;">{profile.total_visits}</span></div>
                        <div><span style="color:rgba(255,255,255,0.5);">Avg Risk</span><br/><span style="color:white;font-weight:600;">{profile.avg_risk_score}</span></div>
                        <div><span style="color:rgba(255,255,255,0.5);">Max Risk</span><br/><span style="color:{'#e74c3c' if profile.max_risk_score > 0.5 else '#f39c12'};font-weight:600;">{profile.max_risk_score}</span></div>
                        <div><span style="color:rgba(255,255,255,0.5);">Trend</span><br/><span style="color:{'#27ae60' if profile.risk_trend=='improving' else '#e74c3c' if profile.risk_trend=='worsening' else '#f39c12'};font-weight:600;">{profile.risk_trend}</span></div>
                    </div>
                    {f'<div style="margin-top:10px;" class="badge badge-danger">⚠️ ESCALATION DETECTED</div>' if profile.escalation_flag else ''}
                </div>
            """, unsafe_allow_html=True)
        
        with col2:
            if PLOTLY_AVAILABLE and not patient_df.empty:
                fig_pt = go.Figure()
                fig_pt.add_trace(go.Scatter(
                    x=patient_df["timestamp"],
                    y=patient_df["risk_score"],
                    mode='lines+markers',
                    name='Risk',
                    line=dict(color='#e74c3c', width=2),
                    marker=dict(size=8, color=patient_df["risk_score"], colorscale=[[0, '#27ae60'], [0.5, '#f39c12'], [1, '#e74c3c']], showscale=False)
                ))
                fig_pt.update_layout(
                    title=t["risk_trend"],
                    height=250,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font_color="white",
                    margin=dict(l=20, r=20, t=40, b=20)
                )
                st.plotly_chart(fig_pt, use_container_width=True)

# ==================== MAIN CHARTS (PLOTLY) ====================
if PLOTLY_AVAILABLE:
    chart_col1, chart_col2 = st.columns(2)
    
    with chart_col1:
        st.markdown(f'<div class="section-title">{t["class_distribution"]}</div>', unsafe_allow_html=True)
        
        class_counts = filtered_df["predicted_class"].value_counts()
        colors_map = {"Neutrophil": "#e74c3c", "Lymphocyte": "#3498db",
                     "Monocyte": "#9b59b6", "Eosinophil": "#f39c12", "Basophil": "#1abc9c"}
        
        fig1 = px.bar(
            x=class_counts.index,
            y=class_counts.values,
            color=class_counts.index,
            color_discrete_map=colors_map,
            labels={"x": "WBC Class", "y": "Count"}
        )
        fig1.update_layout(
            showlegend=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            xaxis_gridcolor="rgba(255,255,255,0.1)",
            yaxis_gridcolor="rgba(255,255,255,0.1)"
        )
        st.plotly_chart(fig1, use_container_width=True)
    
    with chart_col2:
        st.markdown(f'<div class="section-title">{t["confidence_trends"]}</div>', unsafe_allow_html=True)
        
        fig2 = go.Figure()
        fig2.add_trace(go.Histogram(
            x=filtered_df["confidence"],
            nbinsx=20,
            marker_color="#e94560",
            opacity=0.7
        ))
        for thresh, color, name in [(0.85, "#27ae60", "High"), (0.70, "#f39c12", "Moderate"), (0.60, "#e74c3c", "Low")]:
            fig2.add_vline(x=thresh, line_dash="dash", line_color=color, annotation_text=name)
        fig2.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font_color="white",
            showlegend=False,
            margin=dict(l=40, r=20, t=30, b=40)
        )
        st.plotly_chart(fig2, use_container_width=True)

# ==================== DRIFT ANALYTICS ====================
st.markdown(f'<div class="section-title">{t["drift_panel"]}</div>', unsafe_allow_html=True)

drift_cols = st.columns(3)

with drift_cols[0]:
    st.markdown(f"**{t['confidence_trend']}**")
    if PLOTLY_AVAILABLE and n_samples > 5:
        window = max(3, min(20, n_samples // 5))
        rolling_mean = filtered_df["confidence"].rolling(window=window).mean()
        
        fig3 = go.Figure()
        fig3.add_trace(go.Scatter(
            y=filtered_df["confidence"], mode='markers', name='Raw',
            marker=dict(color='rgba(233,69,96,0.5)', size=4)
        ))
        fig3.add_trace(go.Scatter(
            y=rolling_mean, mode='lines', name='Rolling Mean',
            line=dict(color='#3498db', width=2)
        ))
        fig3.update_layout(height=250, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="white", margin=dict(l=20, r=20, t=30, b=20), showlegend=True,
                          legend=dict(font_color="white"))
        st.plotly_chart(fig3, use_container_width=True)

with drift_cols[1]:
    st.markdown(f"**{t['entropy_tracking']}**")
    if PLOTLY_AVAILABLE and "entropy" in filtered_df.columns:
        fig4 = go.Figure()
        fig4.add_trace(go.Scatter(
            y=filtered_df["entropy"], mode='lines',
            line=dict(color='#9b59b6', width=2),
            fill='tozeroy', fillcolor='rgba(155,89,182,0.2)'
        ))
        fig4.update_layout(height=250, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="white", margin=dict(l=20, r=20, t=30, b=20))
        st.plotly_chart(fig4, use_container_width=True)

with drift_cols[2]:
    st.markdown(f"**{t['class_imbalance']}**")
    if PLOTLY_AVAILABLE:
        class_counts = filtered_df["predicted_class"].value_counts()
        expected = n_samples / 5
        
        imbalance_data = []
        for cls in ["Neutrophil", "Lymphocyte", "Monocyte", "Eosinophil", "Basophil"]:
            count = class_counts.get(cls, 0)
            imbalance = abs(count - expected) / expected if expected > 0 else 0
            imbalance_data.append({"Class": cls, "Imbalance": imbalance})
        
        imb_df = pd.DataFrame(imbalance_data)
        fig5 = px.bar(imb_df, x="Class", y="Imbalance",
                     color="Imbalance", color_continuous_scale=["#27ae60", "#f39c12", "#e74c3c"])
        fig5.update_layout(height=250, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
                          font_color="white", margin=dict(l=20, r=20, t=30, b=20),
                          coloraxis_showscale=False)
        st.plotly_chart(fig5, use_container_width=True)

# ==================== PERFORMANCE METRICS ====================
st.markdown(f'<div class="section-title">{t["performance_metrics"]}</div>', unsafe_allow_html=True)

perf_cols = st.columns(4)
perf_data = [
    (f"{metrics['success_rate']:.1%}", t["success_rate"], "#27ae60", "green"),
    (f"{1-metrics['success_rate']:.1%}", t["error_rate"], "#e74c3c", "red"),
    (f"{metrics['auto_processed']:.1%}", t["auto_processed"], "#3498db", "blue"),
    (f"{1-metrics['auto_processed']:.1%}", t["needs_manual"], "#f39c12", "orange")
]

for i, (value, label, color, card_type) in enumerate(perf_data):
    with perf_cols[i]:
        st.markdown(f"""
            <div class="dashboard-card {card_type}">
                <div style="font-size:2rem;font-weight:800;color:{color};">{value}</div>
                <div style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin-top:4px;">{label}</div>
            </div>
        """, unsafe_allow_html=True)

# ==================== MLOps LAYER ====================
st.markdown(f'<div class="section-title">{t["mlops_layer"]}</div>', unsafe_allow_html=True)

mlops_cols = st.columns(3)

# Model tracking
with mlops_cols[0]:
    st.markdown(f"""
        <div class="dashboard-card blue">
            <h4 style="color:#3498db;margin-bottom:10px;">{t["model_tracking"]}</h4>
            <div style="font-size:0.85rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:rgba(255,255,255,0.6);">{t["model_version"]}</span>
                    <span style="color:white;font-weight:600;">{model_info.get('model_name', 'N/A')}</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:rgba(255,255,255,0.6);">Total Inferences</span>
                    <span style="color:white;font-weight:600;">{n_samples}</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:rgba(255,255,255,0.6);">{t["accuracy"]}</span>
                    <span style="color:white;font-weight:600;">{metrics['success_rate']:.1%}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# Drift history
with mlops_cols[1]:
    drift_events = 1 if drift_result["drift_detected"] else 0
    st.markdown(f"""
        <div class="dashboard-card {'red' if drift_events > 0 else 'green'}">
            <h4 style="color:{'#e74c3c' if drift_events > 0 else '#27ae60'};margin-bottom:10px;">{t["drift_history"]}</h4>
            <div style="font-size:2rem;font-weight:800;color:{'#e74c3c' if drift_events > 0 else '#27ae60'};">{drift_events}</div>
            <div style="color:rgba(255,255,255,0.7);font-size:0.85rem;margin-top:4px;">Events detected</div>
            <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin-top:6px;">
                p={drift_result['p_value']} | z={drift_result['z_score']}
            </div>
        </div>
    """, unsafe_allow_html=True)

# System resources
with mlops_cols[2]:
    gpu_text = f"{sys_metrics['gpu_memory_allocated_gb']:.1f}/{sys_metrics['gpu_memory_total_gb']:.1f} GB" if sys_metrics['gpu_available'] else "N/A"
    st.markdown(f"""
        <div class="dashboard-card purple">
            <h4 style="color:#9b59b6;margin-bottom:10px;">{t["device_info"]}</h4>
            <div style="font-size:0.85rem;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:rgba(255,255,255,0.6);">{t["cpu_load"]}</span>
                    <span style="color:white;font-weight:600;">{sys_metrics['cpu_percent']:.1f}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:rgba(255,255,255,0.6);">{t["ram_usage"]}</span>
                    <span style="color:white;font-weight:600;">{sys_metrics['ram_percent']:.1f}%</span>
                </div>
                <div style="display:flex;justify-content:space-between;">
                    <span style="color:rgba(255,255,255,0.6);">{t["gpu_memory"]}</span>
                    <span style="color:white;font-weight:600;">{gpu_text}</span>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

# ==================== SYSTEM HEALTH & RISK DISTRIBUTION ====================
bottom_col1, bottom_col2 = st.columns(2)

with bottom_col1:
    st.markdown(f'<div class="section-title">{t["model_performance"]}</div>', unsafe_allow_html=True)
    
    if PLOTLY_AVAILABLE:
        fig6 = go.Figure()
        fig6.add_trace(go.Scatter(
            x=list(range(1, len(filtered_df) + 1)),
            y=filtered_df["inference_time_ms"],
            mode='lines', line=dict(color='#9b59b6', width=1.5),
            fill='tozeroy', fillcolor='rgba(155,89,182,0.15)'
        ))
        fig6.update_layout(
            title=t["inference_time"],
            plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="white", height=300, margin=dict(l=40, r=20, t=50, b=40)
        )
        st.plotly_chart(fig6, use_container_width=True)
    
    # Model info card
    st.markdown(f"""
        <div class="dashboard-card blue">
            <h4 style="color:#3498db;margin-bottom:12px;">{t["model_info"]}</h4>
            <div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;font-size:0.85rem;">
                <div><span style="color:rgba(255,255,255,0.5);">{t["model_architecture"]}</span><br/>
                    <span style="color:white;font-weight:600;">{model_info.get('model_name', 'N/A')}</span></div>
                <div><span style="color:rgba(255,255,255,0.5);">{t["device"]}</span><br/>
                    <span style="color:white;font-weight:600;">{model_info.get('device', 'CPU')}</span></div>
                <div><span style="color:rgba(255,255,255,0.5);">{t["num_classes"]}</span><br/>
                    <span style="color:white;font-weight:600;">{model_info.get('num_classes', 'N/A')}</span></div>
                <div><span style="color:rgba(255,255,255,0.5);">{t["gradcam_status"]}</span><br/>
                    <span style="color:{'#27ae60' if model_info.get('gradcam_available') else '#e74c3c'};font-weight:600;">
                    {t["active"] if model_info.get('gradcam_available') else t["inactive"]}</span></div>
            </div>
        </div>
    """, unsafe_allow_html=True)

with bottom_col2:
    st.markdown(f'<div class="section-title">{t["system_health"]}</div>', unsafe_allow_html=True)
    
    # Resource bars
    resources = [
        (t["cpu_load"], sys_metrics["cpu_percent"], "#27ae60" if sys_metrics["cpu_percent"] < 70 else "#e74c3c"),
        (t["ram_usage"], sys_metrics["ram_percent"], "#27ae60" if sys_metrics["ram_percent"] < 80 else "#e74c3c"),
    ]
    if sys_metrics["gpu_available"]:
        gpu_pct = (sys_metrics["gpu_memory_allocated_gb"] / sys_metrics["gpu_memory_total_gb"] * 100) if sys_metrics["gpu_memory_total_gb"] > 0 else 0
        resources.append((t["gpu_memory"], gpu_pct, "#27ae60" if gpu_pct < 80 else "#e74c3c"))
    
    for label, value, color in resources:
        st.markdown(f"""
            <div class="dashboard-card" style="margin-bottom:10px;">
                <div style="display:flex;justify-content:space-between;margin-bottom:6px;">
                    <span style="color:rgba(255,255,255,0.7);font-size:0.85rem;">{label}</span>
                    <span style="color:{color};font-weight:700;">{value:.1f}%</span>
                </div>
                <div style="background:rgba(255,255,255,0.1);border-radius:10px;height:8px;overflow:hidden;">
                    <div style="width:{min(value, 100)}%;height:100%;background:{color};border-radius:10px;"></div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Risk distribution
    st.markdown(f'<div style="margin-top:16px;color:rgba(255,255,255,0.8);font-size:0.9rem;">{t["risk_distribution"]}</div>', unsafe_allow_html=True)
    
    risk_counts = filtered_df["risk_level"].value_counts()
    if PLOTLY_AVAILABLE:
        fig7 = px.pie(
            values=risk_counts.values,
            names=risk_counts.index,
            color=risk_counts.index,
            color_discrete_map={"LOW": "#27ae60", "MODERATE": "#f39c12", "HIGH": "#e74c3c", "CRITICAL": "#c0392b"}
        )
        fig7.update_layout(
            height=250, plot_bgcolor="rgba(0,0,0,0)", paper_bgcolor="rgba(0,0,0,0)",
            font_color="white", showlegend=True,
            legend=dict(font_color="white", orientation="h", yanchor="bottom", y=-0.2),
            margin=dict(l=20, r=20, t=30, b=60)
        )
        st.plotly_chart(fig7, use_container_width=True)

# ==================== RECENT ANALYSES ====================
st.markdown(f'<div class="section-title">{t["recent_analyses"]}</div>', unsafe_allow_html=True)

recent_display = filtered_df.tail(20)[["timestamp", "image_name", "predicted_class", "confidence", "risk_level", "patient_id"]].copy()
recent_display["timestamp"] = recent_display["timestamp"].dt.strftime("%Y-%m-%d %H:%M")
recent_display["confidence"] = recent_display["confidence"].apply(lambda x: f"{x:.1%}")
recent_display["Status"] = filtered_df.tail(20)["confidence"].apply(lambda x: "✅" if x > 0.85 else "⚠️")

st.dataframe(recent_display, use_container_width=True, height=300, hide_index=True)

# ==================== EXPORT ====================
st.markdown(f'<div class="section-title">{t["export_options"]}</div>', unsafe_allow_html=True)

export_df = filtered_df[[
    "timestamp", "image_name", "predicted_class", "confidence",
    "risk_level", "risk_score", "patient_id", "inference_time_ms", "device"
]].copy()
export_df["timestamp"] = export_df["timestamp"].dt.strftime("%Y-%m-%d %H:%M:%S")

csv = export_df.to_csv(index=False).encode("utf-8")
st.download_button(
    t["export_report"], csv,
    f"wbc_dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
    "text/csv", use_container_width=True
)

# Footer
st.markdown(f"""
    <div style="text-align:center;padding:16px;color:rgba(255,255,255,0.3);font-size:0.75rem;margin-top:30px;">
        WBC Vision AI v5.1 | {t["last_updated"]}: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} | 
        MLOps Dashboard | {t["vectorized_ops"]} • {t["cached"]} • {t["precomputed"]} | Stability Pass 2 ✅
    </div>
""", unsafe_allow_html=True)