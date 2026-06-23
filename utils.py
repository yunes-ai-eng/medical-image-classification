"""
WBC Vision AI - Utilities
Grad-CAM, Image Processing, Reports
"""

import torch
import torch.nn.functional as F
import numpy as np
import cv2
import base64
from datetime import datetime
from pathlib import Path
import plotly.graph_objects as go

from config import CLASS_NAMES, CLASS_NAMES_AR, DEVICE, IMG_SIZE


# ==================== GRAD-CAM (FIXED) ====================

class GradCAMGenerator:
    """مولد خرائط الحرارة Grad-CAM - محسن وآمن"""
    
    def __init__(self, model):
        self.model = model
        self.target_layer = model.features[-1]
        self.gradients = None
        self.activations = None
        self._register_hooks()
    
    def _register_hooks(self):
        def forward_hook(module, input, output):
            # ✅ FIX: تخزين مباشر بدون list (منع التراكم)
            self.activations = output.detach()
        
        def backward_hook(module, grad_input, grad_output):
            # ✅ FIX: تخزين مباشر بدون list (منع التراكم)
            self.gradients = grad_output[0].detach()
        
        self.target_layer.register_forward_hook(forward_hook)
        self.target_layer.register_full_backward_hook(backward_hook)
    
    def generate(self, input_tensor, target_class=None):
        """توليد خريطة الحرارة - محسن"""
        # إعادة تعيين القيم
        self.gradients = None
        self.activations = None
        
        output = self.model(input_tensor)
        
        if target_class is None:
            target_class = output.argmax(dim=1).item()
        
        self.model.zero_grad()
        output[0, target_class].backward()
        
        # ✅ SAFETY FIX: التحقق من وجود التدرجات
        if self.gradients is None or self.activations is None:
            raise RuntimeError("Grad-CAM hooks failed. Gradients or activations are None.")
        
        # ✅ FIX: حساب متوسط التدرجات بشكل آمن
        grads = self.gradients  # shape: (1, C, H, W)
        
        # ✅ SAFETY FIX: التعامل مع أي batch size
        if grads.dim() == 4:
            # (batch, channels, height, width)
            pooled_grads = torch.mean(grads, dim=(2, 3))[0]  # متوسط على H, W
        else:
            pooled_grads = torch.mean(grads, dim=(1, 2))  # احتياطي
        
        # ✅ FIX: وزن الخرائط النشطة بشكل صحيح
        activations = self.activations[0]  # (C, H, W)
        
        # التحقق من التوافق
        if activations.shape[0] != pooled_grads.shape[0]:
            raise RuntimeError(f"Shape mismatch: activations {activations.shape}, grads {pooled_grads.shape}")
        
        # الوزن
        weighted_activations = activations * pooled_grads[:, None, None]
        
        # توليد الخريطة
        heatmap = torch.mean(weighted_activations, dim=0).cpu().numpy()
        heatmap = np.maximum(heatmap, 0)
        heatmap /= (np.max(heatmap) + 1e-8)  # تجنب القسمة على صفر
        
        return heatmap, target_class
    
    def overlay_heatmap(self, image: np.ndarray, heatmap: np.ndarray, alpha=0.5):
        """دمج الخريطة مع الصورة"""
        # التحقق من أبعاد الصورة
        if image is None or heatmap is None:
            raise ValueError("Image or heatmap is None")
        
        heatmap_resized = cv2.resize(heatmap, (image.shape[1], image.shape[0]))
        heatmap_colored = cv2.applyColorMap(np.uint8(255 * heatmap_resized), cv2.COLORMAP_JET)
        
        if image.shape[2] == 3:
            image_bgr = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        else:
            image_bgr = image
        
        superimposed = cv2.addWeighted(image_bgr, 1 - alpha, heatmap_colored, alpha, 0)
        return cv2.cvtColor(superimposed, cv2.COLOR_BGR2RGB)


# ==================== PLOTLY CHARTS ====================

def create_probability_chart(predictions: dict, lang="en"):
    """رسم بياني للاحتمالات"""
    classes = list(predictions.keys())
    values = list(predictions.values())
    
    # الألوان
    colors = ["#2E86AB" if v == max(values) else "#A8DADC" for v in values]
    
    # التسميات حسب اللغة
    if lang == "ar":
        labels = [CLASS_NAMES_AR[c] for c in classes]
        title = "📈 توزيع الاحتمالات"
    else:
        labels = classes
        title = "📈 Probability Distribution"
    
    fig = go.Figure(data=[go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1%}" for v in values],
        textposition="outside",
        textfont=dict(size=14)
    )])
    
    fig.update_layout(
        title=dict(text=title, font=dict(size=18, color="#2E86AB")),
        xaxis=dict(title="Probability" if lang=="en" else "الاحتمال", range=[0, 1.05], tickformat=".0%"),
        yaxis=dict(title=""),
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=120, r=30, t=60, b=40),
        showlegend=False
    )
    
    return fig


def create_gauge_chart(confidence: float, lang="en"):
    """عداد الثقة"""
    color = "#28a745" if confidence >= 0.85 else "#ffc107" if confidence >= 0.70 else "#dc3545"
    
    title = "Confidence" if lang == "en" else "الثقة"
    
    fig = go.Figure(data=[go.Indicator(
        mode="gauge+number",
        value=confidence * 100,
        number={"suffix": "%", "font": {"size": 40, "color": color}},
        title={"text": title, "font": {"size": 16}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1},
            "bar": {"color": color, "thickness": 0.75},
            "bgcolor": "white",
            "borderwidth": 2,
            "steps": [
                {"range": [0, 70], "color": "#ffebee"},
                {"range": [70, 85], "color": "#fff8e1"},
                {"range": [85, 100], "color": "#e8f5e9"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 4},
                "thickness": 0.8,
                "value": 85
            }
        }
    )])
    
    fig.update_layout(height=300, margin=dict(l=20, r=20, t=50, b=20), paper_bgcolor="rgba(0,0,0,0)")
    return fig


# ==================== REPORT GENERATOR ====================

class MedicalReportGenerator:
    """مولد التقارير الطبية"""
    
    def __init__(self, lang="en"):
        self.lang = lang
    
    def generate_html_report(self, result, patient_name="", patient_id=""):
        """توليد تقرير HTML"""
        
        predicted = result["predicted_class"]
        confidence = result["confidence"]
        probs = result["predictions"]
        
        # معرف التقرير
        report_id = f"WBC-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        
        # بناء شريط الاحتمالات
        prob_bars = ""
        for cls, prob in probs.items():
            pct = prob * 100
            color = "#28a745" if cls == predicted else "#6c757d"
            label = CLASS_NAMES_AR[cls] if self.lang == "ar" else cls
            
            prob_bars += f"""
            <div style="margin: 8px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 4px;">
                    <span><strong>{label}</strong></span>
                    <span>{prob:.3f} ({pct:.1f}%)</span>
                </div>
                <div style="background: #e9ecef; border-radius: 10px; height: 24px; overflow: hidden;">
                    <div style="background: {color}; width: {pct}%; height: 100%; border-radius: 10px; 
                                display: flex; align-items: center; justify-content: flex-end; 
                                padding-right: 8px; color: white; font-size: 12px;">
                        {pct:.1f}%
                    </div>
                </div>
            </div>
            """
        
        # اللغة والاتجاه
        dir_attr = "rtl" if self.lang == "ar" else "ltr"
        lang_attr = "ar" if self.lang == "ar" else "en"
        
        # النصوص
        if self.lang == "ar":
            title = "التقرير الطبي لتصنيف خلايا الدم البيضاء"
            report_id_label = "معرف التقرير"
            date_label = "التاريخ"
            diagnosis_label = "التشخيص الرئيسي"
            confidence_label = "نسبة الثقة"
            prob_dist_label = "توزيع الاحتمالات"
            disclaimer = "هذه الأداة تساعد في التشخيص. المراجعة النهائية تتطلب أخصائي أمراض دم."
        else:
            title = "WBC Classification Medical Report"
            report_id_label = "Report ID"
            date_label = "Date"
            diagnosis_label = "Primary Diagnosis"
            confidence_label = "Confidence"
            prob_dist_label = "Probability Distribution"
            disclaimer = "This tool assists in diagnosis. Final review requires a hematologist."
        
        html = f"""
        <!DOCTYPE html>
        <html dir="{dir_attr}" lang="{lang_attr}">
        <head>
            <meta charset="UTF-8">
            <title>WBC Report - {report_id}</title>
            <style>
                body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f5f7fa; 
                       margin: 0; padding: 20px; color: #333; }}
                .container {{ max-width: 800px; margin: 0 auto; background: white; 
                              border-radius: 16px; box-shadow: 0 4px 20px rgba(0,0,0,0.1); padding: 40px; }}
                .header {{ text-align: center; border-bottom: 3px solid #2E86AB; padding-bottom: 20px; margin-bottom: 30px; }}
                .header h1 {{ color: #2E86AB; margin: 0; font-size: 28px; }}
                .diagnosis-box {{ background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); 
                                  color: white; padding: 30px; border-radius: 16px; 
                                  text-align: center; margin: 20px 0; }}
                .diagnosis-box h2 {{ margin: 0; font-size: 32px; }}
                .section {{ margin: 25px 0; padding: 20px; background: #fafbfc; border-radius: 12px; }}
                .section h3 {{ color: #2E86AB; margin-top: 0; }}
                .footer {{ text-align: center; margin-top: 30px; padding-top: 20px; 
                           border-top: 1px solid #e9ecef; color: #999; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🔬 {title}</h1>
                    <p>{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
                </div>
                
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 15px; margin: 20px 0;">
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                        <small style="color: #666;">{report_id_label}</small><br>
                        <strong style="font-size: 16px;">{report_id}</strong>
                    </div>
                    <div style="background: #f8f9fa; padding: 15px; border-radius: 8px;">
                        <small style="color: #666;">{date_label}</small><br>
                        <strong style="font-size: 16px;">{datetime.now().strftime('%Y-%m-%d')}</strong>
                    </div>
                </div>
                
                <div class="diagnosis-box">
                    <h2>{CLASS_NAMES_AR[predicted] if self.lang == 'ar' else predicted}</h2>
                    <p style="font-size: 20px; margin: 10px 0 0;">{confidence_label}: {confidence:.2%}</p>
                </div>
                
                <div class="section">
                    <h3>{prob_dist_label}</h3>
                    {prob_bars}
                </div>
                
                <div class="footer">
                    <p>{disclaimer}</p>
                    <p>WBC Vision AI v2.0 | EfficientNet-V2-S</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        return html


# ==================== HELPER FUNCTIONS ====================

def get_status_indicator(confidence: float, threshold=0.85):
    """مؤشر حالة الثقة"""
    if confidence >= threshold:
        return "high", "✅"
    elif confidence >= 0.70:
        return "review", "⚠️"
    else:
        return "low", "❌"


def get_status_text(status: str, lang="en"):
    """نص الحالة حسب اللغة"""
    texts = {
        "high": {"en": "High Confidence", "ar": "ثقة عالية"},
        "review": {"en": "Review Required", "ar": "يتطلب مراجعة"},
        "low": {"en": "Low Confidence", "ar": "ثقة منخفضة"}
    }
    return texts.get(status, {}).get(lang, status)