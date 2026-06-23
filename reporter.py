"""
WBC Vision AI - Reporter
Report generation: HTML, CSV, PDF
No model logic, no inference, no evaluation
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional

from config import CLASS_NAMES, CLASS_NAMES_AR, NUM_CLASSES


class ReportGenerator:
    """
    مولد التقارير - منفصل تماماً عن:
    - Model inference
    - Evaluation logic
    - UI / Streamlit
    
    يستقبل النتائج الجاهزة ويولد التقارير
    """
    
    def __init__(self, lang: str = "en", output_dir: str = "reports"):
        """
        Args:
            lang: اللغة ("en" أو "ar")
            output_dir: مجلد حفظ التقارير
        """
        self.lang = lang
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(exist_ok=True)
    
    # ==================== HTML REPORT ====================
    
    def generate_html(self, metrics, per_image: Optional[List[Dict]] = None) -> str:
        """
        توليد تقرير HTML كامل
        
        Args:
            metrics: EvaluationMetrics من evaluator
            per_image: بيانات لكل صورة (اختياري)
        
        Returns:
            str: مسار ملف HTML
        """
        report_id = f"WBC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # بناء المحتوى
        metrics_rows = self._build_metrics_table(metrics)
        cm_html = self._build_confusion_matrix(metrics.confusion_matrix)
        texts = self._get_texts()
        
        # بناء HTML
        html = self._build_html_template(
            report_id=report_id,
            texts=texts,
            metrics=metrics,
            metrics_rows=metrics_rows,
            cm_html=cm_html
        )
        
        # حفظ
        path = self.output_dir / f"report_{report_id}.html"
        path.write_text(html, encoding="utf-8")
        
        print(f"📄 HTML report saved: {path}")
        return str(path)
    
    def _build_html_template(
        self,
        report_id: str,
        texts: Dict,
        metrics,
        metrics_rows: str,
        cm_html: str
    ) -> str:
        """بناء قالب HTML"""
        
        # إحصائيات الأداء
        throughput = metrics.samples_count / metrics.test_duration if metrics.test_duration > 0 else 0
        
        return f"""<!DOCTYPE html>
<html dir="{texts['dir']}" lang="{texts['lang']}">
<head>
    <meta charset="UTF-8">
    <title>WBC Report - {report_id}</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Arial, sans-serif;
            background: linear-gradient(135deg, #f5f7fa 0%, #e4e8ec 100%);
            margin: 0;
            padding: 20px;
            color: #333;
        }}
        .container {{
            max-width: 1000px;
            margin: 0 auto;
            background: white;
            border-radius: 20px;
            box-shadow: 0 10px 40px rgba(0,0,0,0.1);
            overflow: hidden;
        }}
        .header {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 50px 40px;
            text-align: center;
        }}
        .header h1 {{
            margin: 0;
            font-size: 2.5rem;
            font-weight: 700;
        }}
        .header p {{
            margin: 10px 0 0;
            opacity: 0.9;
            font-size: 1.1rem;
        }}
        .content {{
            padding: 40px;
        }}
        .stats-grid {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .stat-card {{
            background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
            padding: 25px;
            border-radius: 16px;
            text-align: center;
            border: 1px solid #dee2e6;
            transition: transform 0.3s;
        }}
        .stat-card:hover {{
            transform: translateY(-5px);
        }}
        .stat-value {{
            font-size: 2.5rem;
            font-weight: 800;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
        }}
        .stat-label {{
            color: #6c757d;
            font-size: 0.9rem;
            margin-top: 5px;
            text-transform: uppercase;
            letter-spacing: 1px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 25px 0;
            border-radius: 12px;
            overflow: hidden;
        }}
        th, td {{
            padding: 15px;
            text-align: center;
            border-bottom: 1px solid #e9ecef;
        }}
        th {{
            background: #2E86AB;
            color: white;
            font-weight: 600;
            text-transform: uppercase;
            font-size: 0.85rem;
            letter-spacing: 1px;
        }}
        tr:hover {{
            background: #f8f9fa;
        }}
        .cm-table th {{
            background: #764ba2;
        }}
        .cm-table td {{
            font-weight: 600;
            font-size: 1.1rem;
        }}
        .section-title {{
            color: #2E86AB;
            font-size: 1.5rem;
            font-weight: 700;
            margin: 35px 0 20px;
            padding-bottom: 10px;
            border-bottom: 3px solid #e9ecef;
        }}
        .footer {{
            text-align: center;
            padding: 30px;
            background: #f8f9fa;
            color: #6c757d;
            font-size: 0.9rem;
            border-top: 1px solid #e9ecef;
        }}
        .badge {{
            display: inline-block;
            padding: 5px 15px;
            border-radius: 20px;
            font-size: 0.85rem;
            font-weight: 600;
        }}
        .badge-success {{
            background: #d4edda;
            color: #155724;
        }}
        .badge-warning {{
            background: #fff3cd;
            color: #856404;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🔬 {texts['title']}</h1>
            <p>{texts['subtitle']} | {datetime.now().strftime('%Y-%m-%d %H:%M')}</p>
        </div>
        
        <div class="content">
            <!-- Report ID -->
            <div style="background: #f8f9fa; padding: 20px; border-radius: 12px; margin-bottom: 30px;">
                <strong>{texts['report_id']}:</strong> <code>{report_id}</code>
            </div>
            
            <!-- Stats -->
            <div class="section-title">📊 {texts['overview']}</div>
            <div class="stats-grid">
                <div class="stat-card">
                    <div class="stat-value">{metrics.accuracy:.2%}</div>
                    <div class="stat-label">{texts['accuracy']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{metrics.balanced_accuracy:.2%}</div>
                    <div class="stat-label">{texts['balanced']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{metrics.samples_count}</div>
                    <div class="stat-label">{texts['samples']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{metrics.test_duration:.1f}s</div>
                    <div class="stat-label">{texts['duration']}</div>
                </div>
                <div class="stat-card">
                    <div class="stat-value">{throughput:.1f}</div>
                    <div class="stat-label">{texts['throughput']}</div>
                </div>
            </div>
            
            <!-- Per-Class Metrics -->
            <div class="section-title">📋 {texts['per_class']}</div>
            <table>
                <thead>
                    <tr>
                        <th>{texts['class']}</th>
                        <th>{texts['precision']}</th>
                        <th>{texts['recall']}</th>
                        <th>{texts['f1']}</th>
                        <th>{texts['support']}</th>
                        <th>{texts['status']}</th>
                    </tr>
                </thead>
                <tbody>
                    {metrics_rows}
                </tbody>
            </table>
            
            <!-- Confusion Matrix -->
            <div class="section-title">🎯 {texts['confusion']}</div>
            <div style="overflow-x: auto;">
                {cm_html}
            </div>
        </div>
        
        <div class="footer">
            <p>{texts['disclaimer']}</p>
            <p><strong>WBC Vision AI v2.0</strong> | EfficientNet-V2-S | {metrics.samples_count} samples</p>
        </div>
    </div>
</body>
</html>"""
    
    # ==================== CSV EXPORT ====================
    
    def generate_csv(self, per_image: List[Dict]) -> str:
        """
        تصدير نتائج لكل صورة إلى CSV
        
        Args:
            per_image: قائمة من dictionaries
        
        Returns:
            str: مسار ملف CSV
        """
        df = pd.DataFrame([
            {
                "Index": r["index"],
                "True Class": r["true_class"],
                "Predicted Class": r["predicted_class"],
                "Correct": r["correct"],
                "Confidence": f"{r['confidence']:.4f}"
            }
            for r in per_image
        ])
        
        path = self.output_dir / f"results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(path, index=False, encoding="utf-8-sig")
        
        print(f"📊 CSV saved: {path}")
        return str(path)
    
    # ==================== PRIVATE HELPERS ====================
    
    def _build_metrics_table(self, metrics) -> str:
        """بناء صفوف جدول المقاييس"""
        rows = ""
        for cls in CLASS_NAMES:
            label = CLASS_NAMES_AR[cls] if self.lang == "ar" else cls
            
            # تحديد الحالة
            f1 = metrics.f1_score[cls]
            if f1 >= 0.95:
                status = '<span class="badge badge-success">Excellent</span>'
            elif f1 >= 0.85:
                status = '<span class="badge badge-success">Good</span>'
            else:
                status = '<span class="badge badge-warning">Review</span>'
            
            rows += f"""
            <tr>
                <td><strong>{label}</strong></td>
                <td>{metrics.precision[cls]:.4f}</td>
                <td>{metrics.recall[cls]:.4f}</td>
                <td>{metrics.f1_score[cls]:.4f}</td>
                <td>{metrics.support[cls]}</td>
                <td>{status}</td>
            </tr>
            """
        return rows
    
    def _build_confusion_matrix(self, cm: np.ndarray) -> str:
        """بناء مصفوفة الارتباك HTML"""
        labels = [CLASS_NAMES_AR[c] if self.lang == "ar" else c for c in CLASS_NAMES]
        
        html = '<table class="cm-table">'
        html += "<tr><th></th>" + "".join(f"<th>{c}</th>" for c in labels) + "</tr>"
        
        for i, cls in enumerate(labels):
            html += f"<tr><th>{cls}</th>"
            for j in range(NUM_CLASSES):
                value = int(cm[i, j])
                if i == j:
                    bg = "#c8e6c9"  # أخضر - صحيح
                elif value > 0:
                    bg = "#ffcdd2"  # أحمر - خطأ
                else:
                    bg = "white"
                
                html += f'<td style="background:{bg}; padding:15px;">{value}</td>'
            html += "</tr>"
        
        html += "</table>"
        return html
    
    def _get_texts(self) -> Dict[str, str]:
        """النصوص حسب اللغة"""
        texts_en = {
            "dir": "ltr", "lang": "en",
            "title": "WBC Classification Report",
            "subtitle": "AI-Powered Hematology Analysis",
            "report_id": "Report ID",
            "overview": "Performance Overview",
            "accuracy": "Accuracy",
            "balanced": "Balanced Accuracy",
            "samples": "Samples",
            "duration": "Duration",
            "throughput": "Images/sec",
            "per_class": "Per-Class Metrics",
            "class": "Class",
            "precision": "Precision",
            "recall": "Recall",
            "f1": "F1-Score",
            "support": "Support",
            "status": "Status",
            "confusion": "Confusion Matrix",
            "disclaimer": "This tool assists in diagnosis. Final review requires a hematologist."
        }
        
        texts_ar = {
            "dir": "rtl", "lang": "ar",
            "title": "تقرير تصنيف خلايا الدم البيضاء",
            "subtitle": "تحليل أمراض الدم بالذكاء الاصطناعي",
            "report_id": "معرف التقرير",
            "overview": "نظرة عامة على الأداء",
            "accuracy": "الدقة",
            "balanced": "الدقة المتوازنة",
            "samples": "العينات",
            "duration": "المدة",
            "throughput": "صورة/ثانية",
            "per_class": "المقاييس لكل فئة",
            "class": "الفئة",
            "precision": "الدقة",
            "recall": "الاستدعاء",
            "f1": "F1",
            "support": "الدعم",
            "status": "الحالة",
            "confusion": "مصفوفة الارتباك",
            "disclaimer": "هذه الأداة تساعد في التشخيص. المراجعة النهائية تتطلب أخصائي أمراض دم."
        }
        
        return texts_ar if self.lang == "ar" else texts_en






# """
# WBC Vision AI - Batch Analysis Page v3.3 (Final Polished)
# Hospital-Grade CDSS - Production Ready
# """

# import streamlit as st
# import pandas as pd
# import numpy as np
# from PIL import Image
# from pathlib import Path
# from datetime import datetime
# import time
# import logging
# from dataclasses import dataclass
# from typing import Dict, List, Optional, Tuple
# from io import BytesIO

# st.set_page_config(
#     page_title="Batch Analysis | Al-Shameeri AI Vision",
#     page_icon="🔬",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# import sys
# sys.path.append(str(Path(__file__).parent.parent))

# from config import *
# from engine import WBCInferenceEngine
# from reporter import ReportGenerator

# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
# logger = logging.getLogger("WBC_Batch")

# @dataclass
# class SystemConfig:
#     ENABLE_ANIMATIONS: bool = True
#     MAX_PREVIEW_IMAGES: int = 6
#     CONFIDENCE_HIGH: float = 0.85
#     CONFIDENCE_MODERATE: float = 0.70
#     CONFIDENCE_LOW: float = 0.60
#     BATCH_SIZE_OPTIONS: List[int] = None
#     MODEL_VERSION: str = "EfficientNet-V2-S-v1.0"
#     MAX_IMAGE_SIZE_MB: int = 10
#     def __post_init__(self):
#         if self.BATCH_SIZE_OPTIONS is None:
#             self.BATCH_SIZE_OPTIONS = [8, 16, 32, 64]

# CONFIG = SystemConfig()

# if "lang" not in st.session_state:
#     st.session_state.lang = "en"

# TEXTS = {
#     "en": {
#         "title": "🔬 Batch Analysis",
#         "subtitle": "Hospital-Grade Multiple Blood Smear Processing with CDSS",
#         "upload_title": "📤 Upload Images",
#         "upload_help": "Select multiple blood smear images (PNG, JPG, JPEG, BMP, TIFF)",
#         "advanced_options": "⚙️ Advanced Options",
#         "confidence_threshold": "Confidence Threshold",
#         "batch_size": "Batch Size",
#         "process_batch": "🚀 Process Batch",
#         "processing": "Processing {current}/{total}...",
#         "results": "📊 Results",
#         "summary": "📈 Summary",
#         "total": "Total",
#         "high_conf": "High Confidence",
#         "review": "Needs Review",
#         "avg_conf": "Average Confidence",
#         "download_csv": "📊 Download CSV",
#         "download_report": "📄 Download HTML Report",
#         "back": "← Back",
#         "disclaimer": "⚠️ AI-assisted CDSS. Final diagnosis requires expert review.",
#         "no_images": "❌ Please upload at least one image",
#         "patient_info": "👤 Patient Info",
#         "clinical": "🏥 Clinical",
#         "risk": "⚠️ Risk",
#         "probabilities": "📊 Probabilities",
#         "model_info": "🤖 Model Info",
#         "processing_complete": "✅ Complete!",
#         "uncertain": "❓ Uncertain",
#         "calibration_warning": "⚠️ Model confidence may not reflect true probability",
#         "audit_log": "📋 Audit Log",
#         "gradcam_toggle": "🔥 Grad-CAM",
#         "export_options": "📤 Export",
#         "class_distribution": "📈 Distribution",
#         "error_processing": "❌ Error: ",
#         "differential": "🔍 Differential",
#         "narrative": "📖 Narrative",
#         "recommendations": "💡 Recommendations",
#         "alerts": "🚨 Alerts",
#         "tab_results": "📊 Results",
#         "tab_clinical": "🏥 Clinical",
#         "tab_export": "📤 Export",
#         "individual_analysis": "🔍 Individual Analysis",
#         "batch_assessment": "📋 Batch Assessment",
#         "attention_needed": "Attention Needed",
#         "avg_risk": "Average Risk",
#         "max_risk": "Max Risk",
#         "processing_time": "Processing Time",
#         "device": "Device",
#         "timestamp": "Timestamp",
#         "model_version": "Model Version",
#         "image_error": "❌ Failed to load image",
#         "image_too_large": "⚠️ Image too large (>{}MB)",
#         "unknown_class": "Unknown",
#         "calibration_score": "Calibration Score",
#         "entropy": "Entropy",
#         "margin": "Margin",
#         "uncertainty_metrics": "📊 Uncertainty Metrics",
#     }
# }

# t = TEXTS[st.session_state.lang]

# st.markdown("""
# <style>
#     .stApp {
#         background: linear-gradient(135deg, #0f0c29 0%, #302b63 50%, #24243e 100%);
#         background-attachment: fixed;
#         font-family: 'Inter', sans-serif;
#     }
#     .main .block-container { max-width: 1400px; padding: 2rem 3rem; }
#     .glass-panel {
#         background: rgba(255,255,255,0.03);
#         backdrop-filter: blur(20px);
#         border: 1px solid rgba(255,255,255,0.08);
#         border-radius: 20px;
#         padding: 24px;
#         color: white;
#     }
#     .medical-card {
#         background: linear-gradient(145deg, rgba(255,255,255,0.05), rgba(255,255,255,0.02));
#         border: 1px solid rgba(255,255,255,0.1);
#         border-radius: 16px;
#         padding: 20px;
#         color: white;
#         position: relative;
#         overflow: hidden;
#     }
#     .medical-card::before {
#         content: '';
#         position: absolute;
#         top: 0; left: 0; right: 0; height: 3px;
#         background: linear-gradient(90deg, #e94560, #ff6b6b);
#     }
#     .medical-card.green::before { background: linear-gradient(90deg, #27ae60, #2ecc71); }
#     .medical-card.yellow::before { background: linear-gradient(90deg, #f39c12, #f1c40f); }
#     .medical-card.red::before { background: linear-gradient(90deg, #e74c3c, #c0392b); }
#     .stat-card {
#         background: rgba(255,255,255,0.05);
#         border: 1px solid rgba(255,255,255,0.1);
#         border-radius: 14px;
#         padding: 18px;
#         text-align: center;
#     }
#     .stat-value {
#         font-size: 2rem;
#         font-weight: 800;
#         background: linear-gradient(135deg, #e94560, #ff6b6b);
#         -webkit-background-clip: text;
#         -webkit-text-fill-color: transparent;
#     }
#     .stat-label { font-size: 0.8rem; color: rgba(255,255,255,0.6); margin-top: 4px; }
#     .section-title {
#         color: #e94560;
#         font-size: 1.3rem;
#         font-weight: 700;
#         margin: 24px 0 12px;
#         padding-bottom: 8px;
#         border-bottom: 2px solid rgba(233,69,96,0.3);
#     }
#     .section-title:first-of-type { margin-top: 0; }
#     .medical-banner {
#         background: linear-gradient(90deg, rgba(255,193,7,0.15), rgba(255,152,0,0.15));
#         border: 1px solid rgba(255,193,7,0.4);
#         border-radius: 14px;
#         padding: 12px 20px;
#         text-align: center;
#         color: #ffc107;
#         font-size: 0.85rem;
#         margin-bottom: 20px;
#     }
#     .input-card {
#         background: rgba(255,255,255,0.03);
#         border: 1px solid rgba(255,255,255,0.08);
#         border-radius: 24px;
#         padding: 40px;
#         backdrop-filter: blur(10px);
#         box-shadow: 0 8px 32px rgba(0,0,0,0.2);
#     }
#     .result-card {
#         background: rgba(255,255,255,0.02);
#         border: 1px solid rgba(255,255,255,0.06);
#         border-radius: 20px;
#         padding: 30px;
#         margin: 20px 0;
#         backdrop-filter: blur(5px);
#     }
#     .back-btn-container { text-align: center; margin-bottom: 20px; }
#     .section-divider {
#         border: none;
#         height: 1px;
#         background: linear-gradient(90deg, transparent, rgba(233,69,96,0.3), transparent);
#         margin: 30px 0;
#     }
#     .confidence-bar {
#         width: 100%;
#         height: 10px;
#         background: rgba(255,255,255,0.1);
#         border-radius: 5px;
#         overflow: hidden;
#     }
#     .confidence-fill {
#         height: 100%;
#         border-radius: 5px;
#         transition: width 0.6s ease;
#     }
#     .badge {
#         display: inline-flex;
#         align-items: center;
#         padding: 3px 10px;
#         border-radius: 12px;
#         font-size: 0.7rem;
#         font-weight: 600;
#     }
#     .badge-success { background: rgba(39,174,96,0.2); color: #2ecc71; border: 1px solid rgba(39,174,96,0.3); }
#     .badge-warning { background: rgba(243,156,18,0.2); color: #f1c40f; border: 1px solid rgba(243,156,18,0.3); }
#     .badge-danger { background: rgba(231,76,60,0.2); color: #e74c3c; border: 1px solid rgba(231,76,60,0.3); }
#     .alert-critical {
#         background: rgba(231,76,60,0.15);
#         border: 1px solid rgba(231,76,60,0.4);
#         border-radius: 12px;
#         padding: 12px 16px;
#         color: #e74c3c;
#     }
#     .alert-warning {
#         background: rgba(243,156,18,0.15);
#         border: 1px solid rgba(243,156,18,0.4);
#         border-radius: 12px;
#         padding: 12px 16px;
#         color: #f1c40f;
#     }
#     div[data-testid="stFileUploader"] > section {
#         background: rgba(0,0,0,0.2);
#         border: 2px dashed rgba(233,69,96,0.4);
#         border-radius: 16px;
#         padding: 30px;
#     }
#     details {
#         background: rgba(0,0,0,0.2) !important;
#         border: 1px solid rgba(255,255,255,0.1) !important;
#         border-radius: 12px !important;
#         margin: 10px 0 !important;
#     }
#     .stButton > button {
#         border-radius: 12px;
#         font-weight: 600;
#         height: 3rem;
#         transition: all 0.3s ease;
#     }
#     .stButton > button[kind="primary"] {
#         background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
#         border: none;
#         box-shadow: 0 4px 15px rgba(233,69,96,0.4);
#     }
#     .stButton > button[kind="primary"]:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 6px 20px rgba(233,69,96,0.6);
#     }
#     #MainMenu, footer, header { visibility: hidden; }
# </style>
# """, unsafe_allow_html=True)

# class MedicalRulesEngine:
#     WBC_RULES = {
#         "Neutrophil": {"range": (40, 70), "risk": "low", "significance": "Primary bacterial defense."},
#         "Lymphocyte": {"range": (20, 40), "risk": "medium", "significance": "Adaptive immunity."},
#         "Monocyte": {"range": (2, 8), "risk": "medium", "significance": "Chronic inflammation."},
#         "Eosinophil": {"range": (1, 4), "risk": "high", "significance": "Allergic & parasitic."},
#         "Basophil": {"range": (0.5, 1.0), "risk": "high", "significance": "Rare, inflammatory."},
#     }
#     @classmethod
#     def get_rule(cls, wbc_class: str) -> Dict:
#         return cls.WBC_RULES.get(wbc_class, {})
#     @classmethod
#     def get_risk_color(cls, risk_level: str) -> str:
#         return {"low": "#27ae60", "medium": "#f39c12", "high": "#e74c3c", "critical": "#c0392b"}.get(risk_level, "#f39c12")

# class UncertaintyCalculator:
#     @staticmethod
#     def entropy(probabilities: Dict[str, float]) -> float:
#         probs = np.array(list(probabilities.values()))
#         probs = probs[probs > 0]
#         n_classes = len(probabilities)
#         max_entropy = np.log2(n_classes) if n_classes > 1 else 1.0
#         raw_entropy = -np.sum(probs * np.log2(probs + 1e-10))
#         return raw_entropy / max_entropy if max_entropy > 0 else 0
#     @staticmethod
#     def margin(probabilities: Dict[str, float]) -> float:
#         sorted_probs = sorted(probabilities.values(), reverse=True)
#         return sorted_probs[0] - sorted_probs[1] if len(sorted_probs) > 1 else 0
#     @staticmethod
#     def calibration_score(confidence: float, normalized_entropy: float) -> float:
#         return confidence * (1 - normalized_entropy)

# class RiskEngine:
#     CLASS_RISK = {"Neutrophil": 0.2, "Lymphocyte": 0.3, "Monocyte": 0.4, "Eosinophil": 0.7, "Basophil": 0.8}
#     def assess(self, prediction: Dict, patient_age: Optional[int] = None) -> Dict:
#         cls = prediction["predicted_class"]
#         conf = prediction["confidence"]
#         probs = prediction.get("probabilities", {})
#         confidence_risk = 1.0 - conf
#         class_risk = self.CLASS_RISK.get(cls, 0.5)
#         unc = UncertaintyCalculator()
#         norm_entropy = unc.entropy(probs)
#         pattern_risk = min(norm_entropy * 2, 1.0)
#         age_factor = 1.2 if patient_age and (patient_age < 18 or patient_age > 65) else 1.0
#         age_component = 0.0 if age_factor == 1.0 else 0.15
#         base_score = (confidence_risk * 0.35 + class_risk * 0.30 + pattern_risk * 0.20)
#         score = (base_score + age_component) * age_factor
#         score = min(score, 1.0)
#         if score < 0.25: level, color, desc = "LOW", "#27ae60", "Normal clinical presentation"
#         elif score < 0.50: level, color, desc = "MODERATE", "#f39c12", "Requires monitoring"
#         elif score < 0.75: level, color, desc = "HIGH", "#e74c3c", "Clinical intervention recommended"
#         else: level, color, desc = "CRITICAL", "#c0392b", "Immediate attention required"
#         return {
#             "score": round(score, 3), "level": level, "color": color, "description": desc,
#             "clinical_interpretation": self._clinical_interpretation(level, cls, conf),
#             "components": {
#                 "confidence_risk": round(confidence_risk, 3), "class_risk": class_risk,
#                 "pattern_risk": round(pattern_risk, 3), "normalized_entropy": round(norm_entropy, 3),
#                 "age_factor": age_factor
#             }
#         }
#     def _clinical_interpretation(self, level: str, cls: str, conf: float) -> str:
#         if level == "LOW": return f"{cls} identified with good confidence ({conf:.1%}). No immediate clinical concerns."
#         elif level == "MODERATE": return f"{cls} detected. Monitor patient and consider follow-up testing."
#         elif level == "HIGH": return f"{cls} with elevated risk profile. Clinical correlation strongly advised."
#         else: return f"Critical risk level for {cls}. Immediate medical evaluation required."
#     def assess_batch(self, predictions: List[Dict]) -> Dict:
#         scores = []
#         distribution = {"LOW": 0, "MODERATE": 0, "HIGH": 0, "CRITICAL": 0}
#         for pred in predictions:
#             risk = self.assess(pred)
#             scores.append(risk["score"])
#             distribution[risk["level"]] += 1
#         return {
#             "avg_score": round(np.mean(scores), 3) if scores else 0,
#             "max_score": round(max(scores), 3) if scores else 0,
#             "distribution": distribution,
#             "attention_needed": distribution["HIGH"] + distribution["CRITICAL"],
#             "total": len(predictions)
#         }

# class ExplanationEngine:
#     def __init__(self, lang: str = "en"):
#         self.lang = lang
#     def generate(self, prediction: Dict, risk: Dict) -> Dict:
#         cls = prediction["predicted_class"]
#         conf = prediction["confidence"]
#         probs = prediction.get("probabilities", {})
#         narrative = self._narrative(cls, conf, risk["level"])
#         recs = self._recommendations(cls, conf, risk)
#         alerts = self._alerts(cls, conf, risk, probs)
#         differential = self._differential(probs)
#         unc = UncertaintyCalculator()
#         norm_entropy = unc.entropy(probs)
#         cal_score = unc.calibration_score(conf, norm_entropy)
#         return {
#             "narrative": narrative, "recommendations": recs, "alerts": alerts,
#             "differential": differential, "calibration_warning": cal_score < 0.5,
#             "calibration_score": round(cal_score, 3),
#             "uncertainty": {"entropy": round(norm_entropy, 3), "margin": round(unc.margin(probs), 3)},
#             "requires_review": conf < CONFIG.CONFIDENCE_LOW or risk["level"] in ["HIGH", "CRITICAL"]
#         }
#     def _narrative(self, cls: str, conf: float, risk_level: str) -> str:
#         if conf >= CONFIG.CONFIDENCE_HIGH:
#             return f"High confidence ({conf:.1%}) {cls} identification. Strong model agreement."
#         elif conf >= CONFIG.CONFIDENCE_MODERATE:
#             return f"Moderate confidence ({conf:.1%}) for {cls}. Lab confirmation recommended."
#         return f"Low confidence ({conf:.1%}) for {cls}. Manual expert review mandatory."
#     def _recommendations(self, cls: str, conf: float, risk: Dict) -> List[str]:
#         base = ["Correlate with CBC", "Review clinical history", "Consider hematopathologist review"]
#         if conf < CONFIG.CONFIDENCE_MODERATE: base.insert(0, "🔴 PRIORITY: Manual microscopic review")
#         if cls == "Basophil": base.append("Evaluate myeloproliferative disorders")
#         elif cls == "Eosinophil": base.append("Investigate parasitic infection/allergy")
#         return base
#     def _alerts(self, cls: str, conf: float, risk: Dict, probs: Dict) -> List[Dict]:
#         alerts = []
#         if conf < CONFIG.CONFIDENCE_LOW: alerts.append({"level": "critical", "icon": "🚨", "title": "Low Confidence", "message": "Do not use for clinical decisions"})
#         if risk["level"] == "CRITICAL": alerts.append({"level": "critical", "icon": "🚨", "title": "Critical Risk", "message": risk["description"]})
#         if cls == "Basophil": alerts.append({"level": "warning", "icon": "⚠️", "title": "Basophil", "message": "Clinically significant finding"})
#         unc = UncertaintyCalculator()
#         if unc.entropy(probs) > 0.6: alerts.append({"level": "warning", "icon": "📊", "title": "High Uncertainty", "message": "Diffuse probability distribution"})
#         return alerts
#     def _differential(self, probabilities: Dict[str, float]) -> List[Dict]:
#         sorted_items = sorted(probabilities.items(), key=lambda x: x[1], reverse=True)[:3]
#         return [{"class": cls, "probability": prob, "risk": MedicalRulesEngine.get_rule(cls).get("risk", "medium")} for cls, prob in sorted_items]
#     def batch_summary(self, predictions: List[Dict]) -> Dict:
#         total = len(predictions)
#         avg_conf = np.mean([p["confidence"] for p in predictions]) if predictions else 0
#         low_conf = sum(1 for p in predictions if p["confidence"] < CONFIG.CONFIDENCE_MODERATE)
#         if avg_conf >= 0.90 and low_conf == 0: assessment = "All samples high confidence. Results reliable."
#         elif avg_conf >= 0.75: assessment = "Most predictions adequate. Review flagged samples."
#         else: assessment = "Multiple low confidence predictions. Expert review required."
#         return {"total": total, "avg_confidence": avg_conf, "low_confidence_count": low_conf, "assessment": assessment, "requires_review": low_conf > 0}

# class AnalysisPipeline:
#     def __init__(self, engine: WBCInferenceEngine, lang: str = "en"):
#         self.engine = engine
#         self.risk_engine = RiskEngine()
#         self.explanation_engine = ExplanationEngine(lang=lang)
#         self.audit_log = []
#     def process_single(self, image_bytes: bytes, image_name: str, patient_age: Optional[int] = None) -> Dict:
#         start_time = time.perf_counter()
#         try:
#             image = Image.open(BytesIO(image_bytes)).convert("RGB")
#         except Exception as e:
#             logger.error(f"Failed to load image {image_name}: {e}")
#             return {"image_name": image_name, "error": str(e), "predicted_class": "ERROR", "confidence": 0.0, "probabilities": {}, "risk": {}, "explanation": {}, "processing_time_ms": 0, "timestamp": datetime.now().isoformat()}
#         try:
#             result = self.engine.predict(image)
#         except Exception as e:
#             logger.error(f"Prediction failed for {image_name}: {e}")
#             return {"image_name": image_name, "error": str(e), "predicted_class": "ERROR", "confidence": 0.0, "probabilities": {}, "risk": {}, "explanation": {}, "processing_time_ms": 0, "timestamp": datetime.now().isoformat()}
#         if not hasattr(result, 'probabilities') or result.probabilities is None:
#             result.probabilities = {}
#         result_dict = {
#             "image_name": image_name, "predicted_class": getattr(result, 'predicted_class', 'Unknown'),
#             "confidence": getattr(result, 'confidence', 0.0), "probabilities": getattr(result, 'probabilities', {}),
#         }
#         risk = self.risk_engine.assess(result_dict, patient_age)
#         result_dict["risk"] = risk
#         explanation = self.explanation_engine.generate(result_dict, risk)
#         result_dict["explanation"] = explanation
#         result_dict["processing_time_ms"] = round((time.perf_counter() - start_time) * 1000, 2)
#         result_dict["timestamp"] = datetime.now().isoformat()
#         result_dict["model_version"] = CONFIG.MODEL_VERSION
#         self._audit(result_dict)
#         return result_dict
#     def process_batch(self, image_items: List[Tuple[str, bytes]], patient_age: Optional[int] = None, progress_callback=None) -> List[Dict]:
#         results = []
#         for i, (name, img_bytes) in enumerate(image_items):
#             result = self.process_single(img_bytes, name, patient_age)
#             results.append(result)
#             if progress_callback: progress_callback(i + 1, len(image_items))
#         return results
#     def _audit(self, result: Dict):
#         self.audit_log.append({
#             "timestamp": result.get("timestamp", ""), "image": result.get("image_name", ""),
#             "prediction": result.get("predicted_class", ""), "confidence": result.get("confidence", 0),
#             "risk_level": result.get("risk", {}).get("level", "UNKNOWN"),
#             "requires_review": result.get("explanation", {}).get("requires_review", False)
#         })
#     def get_audit_log(self) -> List[Dict]:
#         return self.audit_log

# def render_confidence_bar(confidence: float, width: str = "100%") -> str:
#     pct = int(confidence * 100)
#     color = "#27ae60" if confidence >= CONFIG.CONFIDENCE_HIGH else "#f39c12" if confidence >= CONFIG.CONFIDENCE_MODERATE else "#e74c3c"
#     return f'<div style="display:flex;align-items:center;gap:8px;width:{width};"><div class="confidence-bar" style="flex:1;"><div class="confidence-fill" style="width:{pct}%;background:{color};"></div></div><span style="color:{color};font-weight:700;font-size:0.85rem;min-width:36px;">{pct}%</span></div>'

# def get_status_badge(confidence: float, lang: str = "en") -> Tuple[str, str]:
#     if confidence >= CONFIG.CONFIDENCE_HIGH: return ("✅ High", "success")
#     elif confidence >= CONFIG.CONFIDENCE_MODERATE: return ("⚠️ Moderate", "warning")
#     return ("❌ Review", "danger")

# # ==================== HEADER ====================
# st.markdown(f'<div class="medical-banner">{t["disclaimer"]}</div>', unsafe_allow_html=True)
# st.markdown(f"""
#     <div style="text-align:center;margin-bottom:24px;">
#         <h1 style="color:white;font-size:2.6rem;font-weight:800;margin-bottom:6px;">{t["title"]}</h1>
#         <p style="color:rgba(255,255,255,0.55);font-size:1rem;">{t["subtitle"]}</p>
#     </div>
# """, unsafe_allow_html=True)
# st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
# if st.button(t["back"], key="back_batch"): st.switch_page("app.py")
# st.markdown('</div>', unsafe_allow_html=True)

# @st.cache_resource(show_spinner=False)
# def load_model():
#     return WBCInferenceEngine()

# try:
#     engine = load_model()
# except Exception as e:
#     st.error(f"❌ Model Error: {str(e)}")
#     logger.error(f"Model loading failed: {e}")
#     st.stop()

# for key in ["batch_results", "pipeline", "patient_info", "valid_files_list"]:
#     if key not in st.session_state:
#         st.session_state[key] = None if key not in ["patient_info", "valid_files_list"] else {}

# # ═══════════════════════════════════════════════════════
# # INPUT SECTION (Centered)
# # ═══════════════════════════════════════════════════════
# left_spacer, col_input, right_spacer = st.columns([1.2, 2.2, 1.2])
# with left_spacer: st.empty()
# with right_spacer: st.empty()
# with col_input:
#     st.markdown('<div class="input-card">', unsafe_allow_html=True)
#     st.markdown(f'<div class="section-title" style="margin-top: 0;">{t["upload_title"]}</div>', unsafe_allow_html=True)
#     uploaded_files = st.file_uploader(t["upload_help"], type=["png", "jpg", "jpeg", "bmp", "tiff"], accept_multiple_files=True, label_visibility="collapsed")
#     valid_files = []
#     if uploaded_files:
#         for f in uploaded_files:
#             f.seek(0, 2)
#             size_mb = f.tell() / (1024 * 1024)
#             f.seek(0)
#             if size_mb > CONFIG.MAX_IMAGE_SIZE_MB:
#                 st.warning(t["image_too_large"].format(CONFIG.MAX_IMAGE_SIZE_MB))
#                 continue
#             try:
#                 img = Image.open(f)
#                 img.verify()
#                 f.seek(0)
#                 valid_files.append(f)
#             except Exception as e:
#                 st.error(f"{t['image_error']}: {f.name}")
#                 logger.warning(f"Invalid image {f.name}: {e}")
#         if valid_files:
#             st.success(f"✅ {len(valid_files)} valid images")
#             preview = valid_files[:CONFIG.MAX_PREVIEW_IMAGES]
#             pcols = st.columns(min(3, len(preview)))
#             for pc, pf in zip(pcols, preview):
#                 with pc:
#                     pf.seek(0)
#                     st.image(Image.open(pf), use_container_width=True, caption=pf.name[:12])
#             if len(valid_files) > CONFIG.MAX_PREVIEW_IMAGES:
#                 st.caption(f"+{len(valid_files) - CONFIG.MAX_PREVIEW_IMAGES} more...")
#     st.markdown(f'<div class="section-title">{t["patient_info"]}</div>', unsafe_allow_html=True)
#     labels = {"id": "Patient ID", "name": "Name", "age": "Age", "gender": "Gender", "physician": "Physician"}
#     c1, c2 = st.columns(2)
#     with c1:
#         pat_id = st.text_input(labels["id"], key="p_id")
#         pat_name = st.text_input(labels["name"], key="p_name")
#         pat_age = st.number_input(labels["age"], 0, 120, 30, key="p_age")
#     with c2:
#         pat_gender = st.selectbox(labels["gender"], ["Male", "Female", "Other"], key="p_gender")
#         pat_physician = st.text_input(labels["physician"], key="p_doc")
#     patient_info = {"patient_id": pat_id, "name": pat_name, "age": pat_age, "gender": pat_gender, "physician": pat_physician}
#     st.session_state.patient_info = patient_info
#     with st.expander(t["advanced_options"]):
#         conf_thresh = st.slider(t["confidence_threshold"], 0.50, 0.99, 0.85, 0.01)
#         batch_sz = st.selectbox(t["batch_size"], CONFIG.BATCH_SIZE_OPTIONS, index=2)
#         show_gradcam = st.toggle(t["gradcam_toggle"], value=False)
#     run_disabled = not bool(valid_files)
#     process_clicked = st.button(t["process_batch"], type="primary", use_container_width=True, disabled=run_disabled)
#     st.markdown('</div>', unsafe_allow_html=True)

# # ═══════════════════════════════════════════════════════
# # PROCESSING
# # ═══════════════════════════════════════════════════════
# if process_clicked and valid_files:
#     pipeline = AnalysisPipeline(engine, lang=st.session_state.lang)
#     image_items = []
#     for f in valid_files:
#         try:
#             f.seek(0)
#             image_items.append((f.name, f.read()))
#         except Exception as e:
#             logger.error(f"Failed to read {f.name}: {e}")
#             st.error(f"{t['error_processing']}{f.name}")
#     if not image_items:
#         st.error(t["no_images"])
#     else:
#         progress_bar = st.progress(0)
#         status = st.empty()
#         def update_progress(current, total):
#             progress_bar.progress(current / total)
#             status.markdown(f'<div style="color:white;"><span>🔍</span> <span>{t["processing"].format(current=current, total=total)}</span></div>', unsafe_allow_html=True)
#         try:
#             results = pipeline.process_batch(image_items, patient_age=patient_info.get("age"), progress_callback=update_progress)
#             status.success(t["processing_complete"])
#             progress_bar.empty()
#             st.session_state.batch_results = results
#             st.session_state.pipeline = pipeline
#             st.session_state.valid_files_list = valid_files
#         except Exception as e:
#             logger.error(f"Batch processing failed: {e}")
#             st.error(f"{t['error_processing']}{str(e)}")

# # ═══════════════════════════════════════════════════════
# # RESULTS TABS
# # ═══════════════════════════════════════════════════════
# if st.session_state.batch_results:
#     results = st.session_state.batch_results
#     pipeline = st.session_state.pipeline
#     valid_results = [r for r in results if r.get("predicted_class") != "ERROR" and "error" not in r]
#     error_results = [r for r in results if r.get("predicted_class") == "ERROR" or "error" in r]
#     st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
#     tab_results, tab_clinical, tab_export = st.tabs([t["tab_results"], t["tab_clinical"], t["tab_export"]])
    
#     # ═══════════════════════════════════════════════
#     # TAB 1: RESULTS
#     # ═══════════════════════════════════════════════
#     with tab_results:
#         if error_results:
#             with st.expander(f"⚠️ {len(error_results)} Failed Images"):
#                 for er in error_results: st.error(f"{er['image_name']}: {er.get('error', 'Unknown error')}")
#         if not valid_results:
#             st.warning("No valid predictions. Please check your images.")
#         else:
#             total = len(valid_results)
#             avg_conf = np.mean([r["confidence"] for r in valid_results])
#             high_conf = sum(1 for r in valid_results if r["confidence"] >= CONFIG.CONFIDENCE_HIGH)
#             review_needed = sum(1 for r in valid_results if r["confidence"] < CONFIG.CONFIDENCE_MODERATE)
#             st.markdown(f'<div class="section-title">{t["summary"]}</div>', unsafe_allow_html=True)
#             scols = st.columns(4)
#             stats = [(str(total), t["total"], "📁"), (str(high_conf), t["high_conf"], "✅"), (str(review_needed), t["review"], "⚠️"), (f"{avg_conf:.1%}", t["avg_conf"], "📊")]
#             for i, (val, lbl, icon) in enumerate(stats):
#                 with scols[i]:
#                     st.markdown(f'<div class="stat-card"><div style="font-size:1.3rem;margin-bottom:2px;">{icon}</div><div class="stat-value">{val}</div><div class="stat-label">{lbl}</div></div>', unsafe_allow_html=True)
#             batch_summary = pipeline.explanation_engine.batch_summary(valid_results)
#             st.markdown(f"""
#                 <div class="glass-panel" style="margin-top:16px;">
#                     <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:8px;">
#                         <span style="color:#e94560;font-weight:700;">{t["batch_assessment"]}</span>
#                         <span class="badge badge-{'danger' if batch_summary['requires_review'] else 'success'}">
#                             {'Review Required' if batch_summary['requires_review'] else 'All Clear'}
#                         </span>
#                     </div>
#                     <p style="color:rgba(255,255,255,0.8);font-size:0.9rem;margin:0;">{batch_summary["assessment"]}</p>
#                 </div>
#             """, unsafe_allow_html=True)
#             st.markdown(f'<div class="section-title">{t["class_distribution"]}</div>', unsafe_allow_html=True)
#             class_counts = {}
#             for r in valid_results:
#                 cls = r["predicted_class"]
#                 class_counts[cls] = class_counts.get(cls, 0) + 1
#             dcols = st.columns(max(1, len(class_counts)))
#             colors = {"Neutrophil": "#e74c3c", "Lymphocyte": "#3498db", "Monocyte": "#9b59b6", "Eosinophil": "#f39c12", "Basophil": "#1abc9c"}
#             for i, (cls, count) in enumerate(class_counts.items()):
#                 with dcols[i % len(dcols)]:
#                     pct = (count / total) * 100
#                     st.markdown(f'<div class="glass-panel" style="text-align:center;padding:14px;"><div style="font-size:1.8rem;font-weight:800;color:{colors.get(cls, "#fff")};">{count}</div><div style="color:rgba(255,255,255,0.7);font-size:0.85rem;">{cls}</div><div style="color:rgba(255,255,255,0.5);font-size:0.75rem;">{pct:.1f}%</div></div>', unsafe_allow_html=True)
#             st.markdown(f'<div class="section-title">{t["results"]}</div>', unsafe_allow_html=True)
#             table_data = []
#             for idx, r in enumerate(valid_results):
#                 status_text, badge_type = get_status_badge(r["confidence"], st.session_state.lang)
#                 table_data.append({"#": idx + 1, "Image": r["image_name"], "Class": r["predicted_class"], "Confidence": f"{r['confidence']:.1%}", "Risk": r["risk"]["level"], "Status": status_text})
#             st.dataframe(pd.DataFrame(table_data), use_container_width=True, height=350)
    
#     # ═══════════════════════════════════════════════
#     # TAB 2: CLINICAL
#     # ═══════════════════════════════════════════════
#     with tab_clinical:
#         if not valid_results:
#             st.info("No clinical data available.")
#         else:
#             st.markdown(f'<div class="section-title">{t["risk"]}</div>', unsafe_allow_html=True)
#             batch_risk = pipeline.risk_engine.assess_batch(valid_results)
#             rcols = st.columns(3)
#             risk_data = [
#                 (t["avg_risk"], batch_risk["avg_score"], "#e74c3c" if batch_risk["avg_score"] > 0.5 else "#f39c12" if batch_risk["avg_score"] > 0.25 else "#27ae60", "red" if batch_risk["avg_score"] > 0.5 else "yellow" if batch_risk["avg_score"] > 0.25 else "green"),
#                 (t["attention_needed"], batch_risk["attention_needed"], "#e74c3c", "red" if batch_risk["attention_needed"] > 0 else "green"),
#                 (t["max_risk"], batch_risk["max_score"], "#e74c3c" if batch_risk["max_score"] > 0.5 else "#f39c12" if batch_risk["max_score"] > 0.25 else "#27ae60", "red" if batch_risk["max_score"] > 0.5 else "yellow" if batch_risk["max_score"] > 0.25 else "green")
#             ]
#             for i, (title, value, color, card_type) in enumerate(risk_data):
#                 with rcols[i]:
#                     st.markdown(f'<div class="medical-card {card_type}"><div style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin-bottom:4px;">{title}</div><div style="font-size:1.8rem;font-weight:800;color:{color};">{value}</div></div>', unsafe_allow_html=True)
#             st.markdown(f'<div class="section-title">{t["individual_analysis"]}</div>', unsafe_allow_html=True)
#             for r in valid_results:
#                 exp = r["explanation"]
#                 risk = r["risk"]
#                 with st.expander(f"📷 {r['image_name']} — {r['predicted_class']} ({r['confidence']:.1%})"):
#                     if exp["alerts"]:
#                         for alert in exp["alerts"]:
#                             alert_class = "alert-critical" if alert["level"] == "critical" else "alert-warning"
#                             st.markdown(f'<div class="{alert_class}" style="margin-bottom:8px;"><div style="display:flex;align-items:center;gap:8px;font-weight:700;"><span>{alert["icon"]}</span><span>{alert["title"]}</span></div><div style="font-size:0.85rem;margin-top:4px;opacity:0.9;">{alert["message"]}</div></div>', unsafe_allow_html=True)
#                     if exp["calibration_warning"]: st.warning(t["calibration_warning"])
#                     icols = st.columns([1, 1])
#                     with icols[0]:
#                         st.markdown(f"""
#                             <div class="medical-card">
#                                 <h4 style="color:#e94560;margin-bottom:10px;">🎯 Prediction</h4>
#                                 <div style="font-size:1.3rem;font-weight:700;color:white;">{r['predicted_class']}</div>
#                                 {render_confidence_bar(r['confidence'])}
#                                 <div style="margin-top:10px;color:rgba(255,255,255,0.6);font-size:0.8rem;">
#                                     {t["processing_time"]}: {r['processing_time_ms']}ms
#                                 </div>
#                             </div>
#                         """, unsafe_allow_html=True)
#                         st.markdown(f"""
#                             <div class="medical-card {'red' if risk['level'] in ['HIGH','CRITICAL'] else 'yellow' if risk['level']=='MODERATE' else 'green'}" style="margin-top:10px;">
#                                 <h4 style="color:white;margin-bottom:8px;">⚠️ {t["risk"]}</h4>
#                                 <div style="font-size:1.2rem;font-weight:700;color:{risk['color']};">{risk['level']}</div>
#                                 <div style="color:rgba(255,255,255,0.7);font-size:0.8rem;margin-top:4px;">{risk['description']}</div>
#                                 <div style="color:rgba(255,255,255,0.5);font-size:0.75rem;margin-top:6px;">{t["calibration_score"]}: {exp['calibration_score']}</div>
#                             </div>
#                         """, unsafe_allow_html=True)
#                     with icols[1]:
#                         st.markdown(f"""
#                             <div class="medical-card">
#                                 <h4 style="color:#e94560;margin-bottom:10px;">{t["narrative"]}</h4>
#                                 <p style="color:rgba(255,255,255,0.85);font-size:0.85rem;line-height:1.6;margin:0;">{exp['narrative']}</p>
#                             </div>
#                         """, unsafe_allow_html=True)
#                         st.markdown(f"""
#                             <div class="medical-card" style="margin-top:10px;">
#                                 <h4 style="color:#e94560;margin-bottom:10px;">{t["recommendations"]}</h4>
#                                 <ul style="color:rgba(255,255,255,0.85);font-size:0.8rem;line-height:1.7;padding-left:16px;margin:0;">
#                         """, unsafe_allow_html=True)
#                         for rec in exp["recommendations"]:
#                             st.markdown(f"<li>{rec}</li>", unsafe_allow_html=True)
#                         st.markdown("</ul></div>", unsafe_allow_html=True)
#                     st.markdown(f'<div class="section-title" style="margin-top:16px;">{t["uncertainty_metrics"]}</div>', unsafe_allow_html=True)
#                     unc_cols = st.columns(3)
#                     with unc_cols[0]: st.metric(t["entropy"], f"{exp['uncertainty']['entropy']:.3f}")
#                     with unc_cols[1]: st.metric(t["margin"], f"{exp['uncertainty']['margin']:.3f}")
#                     with unc_cols[2]: st.metric(t["calibration_score"], f"{exp['calibration_score']:.3f}")
#                     st.markdown(f"**{t['differential']}:**")
#                     diff_df = pd.DataFrame(exp["differential"])
#                     if not diff_df.empty:
#                         diff_df["probability"] = diff_df["probability"].apply(lambda x: f"{x:.1%}")
#                         st.dataframe(diff_df, use_container_width=True, hide_index=True)
#                     st.markdown(f"**{t['probabilities']}:**")
#                     for cls, prob in sorted(r["probabilities"].items(), key=lambda x: x[1], reverse=True):
#                         is_pred = cls == r["predicted_class"]
#                         p_color = "#e94560" if is_pred else "rgba(255,255,255,0.25)"
#                         t_color = "#e94560" if is_pred else "rgba(255,255,255,0.6)"
#                         w = "700" if is_pred else "400"
#                         st.markdown(f'<div style="display:flex;align-items:center;gap:8px;margin-bottom:4px;"><span style="min-width:90px;color:{t_color};font-weight:{w};font-size:0.8rem;">{cls}</span><div class="confidence-bar" style="flex:1;"><div class="confidence-fill" style="width:{int(prob*100)}%;background:{p_color};"></div></div><span style="min-width:36px;color:{t_color};font-weight:{w};font-size:0.75rem;text-align:right;">{prob:.1%}</span></div>', unsafe_allow_html=True)
    
#     # ═══════════════════════════════════════════════
#     # TAB 3: EXPORT
#     # ═══════════════════════════════════════════════
#     with tab_export:
#         if not valid_results:
#             st.info("No data to export.")
#         else:
#             st.markdown(f'<div class="section-title">{t["export_options"]}</div>', unsafe_allow_html=True)
#             ecols = st.columns(2)
#             with ecols[0]:
#                 df_exp = pd.DataFrame([
#                     {
#                         "Image": r["image_name"], "Class": r["predicted_class"],
#                         "Confidence": r["confidence"], "Risk_Level": r["risk"]["level"],
#                         "Risk_Score": r["risk"]["score"],
#                         "Requires_Review": r["explanation"]["requires_review"],
#                         "Processing_Time_ms": r["processing_time_ms"],
#                         "Timestamp": r["timestamp"]
#                     }
#                     for r in valid_results
#                 ])
#                 csv = df_exp.to_csv(index=False).encode("utf-8")
#                 st.download_button(t["download_csv"], csv, f"wbc_batch_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv", "text/csv", use_container_width=True)
#             with ecols[1]:
#                 reporter = ReportGenerator(lang=st.session_state.lang)
#                 try:
#                     # ═══ FIXED: استخدام generate_html بدلاً من generate_html_report ═══
#                     result_dicts = []
#                     for r in valid_results:
#                         rd = {
#                             "predicted_class": r["predicted_class"],
#                             "confidence": r["confidence"],
#                             "probabilities": r["probabilities"],
#                             "risk": r["risk"],
#                             "explanation": r["explanation"]
#                         }
#                         result_dicts.append(rd)
#                     # محاولة استخدام generate_html للنتيجة الأولى
#                     if hasattr(reporter, 'generate_html'):
#                         html_path = reporter.generate_html(
#                             result=result_dicts[0],
#                             patient_name=st.session_state.get("patient_info", {}).get("name", ""),
#                             patient_id=st.session_state.get("patient_info", {}).get("patient_id", "")
#                         )
#                         with open(html_path, "r", encoding="utf-8") as f:
#                             html_content = f.read()
#                         st.download_button(
#                             t["download_report"], html_content.encode("utf-8"),
#                             f"wbc_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
#                             "text/html", use_container_width=True
#                         )
#                     else:
#                         st.error("ReportGenerator does not have generate_html method")
#                 except Exception as e:
#                     st.error(f"Report generation failed: {e}")
#             st.markdown(f'<div class="section-title">{t["audit_log"]}</div>', unsafe_allow_html=True)
#             audit_df = pd.DataFrame(pipeline.get_audit_log())
#             if not audit_df.empty:
#                 st.dataframe(audit_df, use_container_width=True, height=200)
    
#     with st.expander(t["model_info"]):
#         st.json({
#             "Model": CONFIG.MODEL_VERSION,
#             "Confidence Thresholds": {"High": CONFIG.CONFIDENCE_HIGH, "Moderate": CONFIG.CONFIDENCE_MODERATE, "Low": CONFIG.CONFIDENCE_LOW},
#             "Total Processed": len(valid_results), "Failed": len(error_results),
#             "System": "WBC Vision AI CDSS v3.3"
#         })

# st.markdown("""
#     <div style="text-align:center;padding:16px;color:rgba(255,255,255,0.3);font-size:0.75rem;margin-top:30px;">
#         WBC Vision AI v3.3 | Al-Shameeri Medical AI | Clinical Decision Support System
#     </div>
# """, unsafe_allow_html=True)
