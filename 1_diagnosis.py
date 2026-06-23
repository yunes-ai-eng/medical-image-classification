
# """
# WBC Vision AI - Single Diagnosis Page (Centered Layout)
# """

# import streamlit as st
# import numpy as np
# from PIL import Image
# from pathlib import Path
# import plotly.graph_objects as go
# from datetime import datetime
# from dataclasses import asdict

# st.set_page_config(
#     page_title="Single Diagnosis | Al-Shameeri AI Vision",
#     page_icon="🔬",
#     layout="wide",
#     initial_sidebar_state="collapsed"
# )

# import sys
# sys.path.append(str(Path(__file__).parent.parent))

# from config import *
# from engine import WBCInferenceEngine
# from utils import get_status_indicator, get_status_text
# from reporter import ReportGenerator

# if "lang" not in st.session_state:
#     st.session_state.lang = "en"

# TEXTS = {
#     "en": {
#         "title": "🔬 Single Cell Diagnosis",
#         "subtitle": "Upload a blood smear image for instant AI analysis",
#         "upload_title": "📤 Upload Image",
#         "upload_help": "Supported formats: PNG, JPG, JPEG, BMP, TIFF",
#         "advanced_options": "⚙️ Advanced Options",
#         "confidence_threshold": "Confidence Threshold",
#         "tta": "Test-Time Augmentation (TTA)",
#         "run_diagnosis": "🚀 Run AI Diagnosis",
#         "processing": "🔍 Analyzing image...",
#         "results": "📊 Diagnosis Results",
#         "predicted_class": "Predicted Class",
#         "confidence": "Confidence",
#         "status": "Status",
#         "gradcam_title": "🎯 Grad-CAM Analysis",
#         "gradcam_desc": "Heatmap shows regions the AI focused on",
#         "probabilities": "📈 Probability Distribution",
#         "clinical_report": "📝 Clinical Report",
#         "description": "Description",
#         "normal_range": "Normal Range",
#         "recommendations": "Recommendations",
#         "download_report": "📄 Download Medical Report",
#         "patient_info": "👤 Patient Information (Optional)",
#         "patient_name": "Patient Name",
#         "patient_id": "Patient ID",
#         "back_home": "← Back to Home",
#         "medical_disclaimer": "⚠️ This is an AI-assisted tool. Final diagnosis requires expert review.",
#         "error_no_image": "❌ Please upload an image first",
#         "error_processing": "❌ Error processing image: ",
#     },
#     "ar": {
#         "title": "🔬 التشخيص الفردي",
#         "subtitle": "ارفع صورة مسحة دم للتحليل الفوري بالذكاء الاصطناعي",
#         "upload_title": "📤 رفع الصورة",
#         "upload_help": "الصيغ المدعومة: PNG, JPG, JPEG, BMP, TIFF",
#         "advanced_options": "⚙️ خيارات متقدمة",
#         "confidence_threshold": "عتبة الثقة",
#         "tta": "تعزيز وقت الاختبار (TTA)",
#         "run_diagnosis": "🚀 تشغيل التشخيص الذكي",
#         "processing": "🔍 جاري تحليل الصورة...",
#         "results": "📊 نتائج التشخيص",
#         "predicted_class": "الفئة المتوقعة",
#         "confidence": "نسبة الثقة",
#         "status": "الحالة",
#         "gradcam_title": "🎯 تحليل Grad-CAM",
#         "gradcam_desc": "الخريطة الحرارية تظهر المناطق التي ركز عليها الذكاء الاصطناعي",
#         "probabilities": "📈 توزيع الاحتمالات",
#         "clinical_report": "📝 التقرير السريري",
#         "description": "الوصف",
#         "normal_range": "النطاق الطبيعي",
#         "recommendations": "التوصيات",
#         "download_report": "📄 تحميل التقرير الطبي",
#         "patient_info": "👤 معلومات المريض (اختياري)",
#         "patient_name": "اسم المريض",
#         "patient_id": "رقم المريض",
#         "back_home": "← العودة للرئيسية",
#         "medical_disclaimer": "⚠️ هذه أداة مساعدة بالذكاء الاصطناعي. التشخيص النهائي يتطلب مراجعة خبير.",
#         "error_no_image": "❌ الرجاء رفع صورة أولاً",
#         "error_processing": "❌ خطأ في معالجة الصورة: ",
#     }
# }

# t = TEXTS[st.session_state.lang]

# st.markdown("""
# <style>
#     .stApp {
#         background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
#         background-attachment: fixed;
#     }
#     /* توسيط المحتوى الرئيسي */
#     .main .block-container {
#         max-width: 1400px;
#         padding: 2rem 3rem;
#     }
#     .diagnosis-box {
#         background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
#         padding: 30px;
#         border-radius: 20px;
#         color: white;
#         text-align: center;
#         box-shadow: 0 15px 35px rgba(17, 153, 142, 0.3);
#         margin: 20px 0;
#     }
#     .diagnosis-box.warning {
#         background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
#         box-shadow: 0 15px 35px rgba(245, 87, 108, 0.3);
#     }
#     .diagnosis-box.caution {
#         background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
#         box-shadow: 0 15px 35px rgba(250, 112, 154, 0.3);
#     }
#     .section-title {
#         color: #e94560;
#         font-size: 1.4rem;
#         font-weight: 700;
#         margin: 25px 0 15px;
#         padding-bottom: 10px;
#         border-bottom: 2px solid rgba(233, 69, 96, 0.3);
#     }
#     .medical-banner {
#         background: linear-gradient(90deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
#         border: 1px solid rgba(255, 193, 7, 0.5);
#         border-radius: 16px;
#         padding: 12px 20px;
#         text-align: center;
#         color: #ffc107;
#         font-size: 0.85rem;
#         margin-bottom: 20px;
#     }
#     /* تحسين بطاقة الإدخال */
#     .input-card {
#         background: rgba(255, 255, 255, 0.03);
#         border: 1px solid rgba(255, 255, 255, 0.08);
#         border-radius: 24px;
#         padding: 35px;
#         backdrop-filter: blur(10px);
#         box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
#     }
#     .input-card:hover {
#         border-color: rgba(233, 69, 96, 0.3);
#         box-shadow: 0 8px 32px rgba(233, 69, 96, 0.1);
#         transition: all 0.3s ease;
#     }
#     /* تنسيق زر الرجوع */
#     .back-btn-container {
#         text-align: center;
#         margin-bottom: 20px;
#     }
#     /* تنسيق عناصر Streamlit */
#     div[data-testid="stFileUploader"] {
#         width: 100%;
#     }
#     div[data-testid="stFileUploader"] > section {
#         background: rgba(0, 0, 0, 0.2);
#         border: 2px dashed rgba(233, 69, 96, 0.4);
#         border-radius: 16px;
#         padding: 30px;
#     }
#     div[data-testid="stFileUploader"] > section:hover {
#         border-color: #e94560;
#         background: rgba(233, 69, 96, 0.05);
#     }
#     /* تنسيق expander */
#     details {
#         background: rgba(0, 0, 0, 0.2) !important;
#         border: 1px solid rgba(255, 255, 255, 0.1) !important;
#         border-radius: 12px !important;
#         margin: 10px 0 !important;
#     }
#     /* تنسيق الأزرار */
#     .stButton > button {
#         border-radius: 12px;
#         font-weight: 600;
#         height: 3rem;
#         transition: all 0.3s ease;
#     }
#     .stButton > button[kind="primary"] {
#         background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
#         border: none;
#         box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
#     }
#     .stButton > button[kind="primary"]:hover {
#         transform: translateY(-2px);
#         box-shadow: 0 6px 20px rgba(233, 69, 96, 0.6);
#     }
#     /* تنسيق slider */
#     div[data-testid="stSlider"] > div {
#         color: white;
#     }
#     /* تنسيق toggle */
#     div[data-testid="stToggle"] {
#         justify-content: flex-start;
#     }
# </style>
# """, unsafe_allow_html=True)

# st.markdown(f'<div class="medical-banner">{t["medical_disclaimer"]}</div>', unsafe_allow_html=True)
# st.markdown(f'<h1 style="color: white; text-align: center; font-size: 2.5rem; font-weight: 800;">{t["title"]}</h1>', unsafe_allow_html=True)
# st.markdown(f'<p style="color: rgba(255,255,255,0.7); text-align: center; font-size: 1.1rem; margin-bottom: 30px;">{t["subtitle"]}</p>', unsafe_allow_html=True)

# # زر الرجوع في المنتصف
# st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
# if st.button(t["back_home"], key="back_home"):
#     st.switch_page("app.py")
# st.markdown('</div>', unsafe_allow_html=True)

# @st.cache_resource(show_spinner=False)
# def load_model():
#     return WBCInferenceEngine()

# try:
#     engine = load_model()
# except Exception as e:
#     st.error(f"❌ Error loading model: {str(e)}")
#     st.stop()

# # ───────────────────────────────────────────────
# # توسيط العمود: [فراغ] [محتوى] [فراغ]
# # ───────────────────────────────────────────────
# left_spacer, col_input, right_spacer = st.columns([1.2, 2.2, 1.2])

# with left_spacer:
#     st.empty()

# with right_spacer:
#     st.empty()

# with col_input:
#     # ─── بطاقة الإدخال الرئيسية ───
#     st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
#     st.markdown(f'<div class="section-title" style="margin-top: 0;">{t["upload_title"]}</div>', unsafe_allow_html=True)
    
#     uploaded_file = st.file_uploader(
#         t["upload_help"],
#         type=["png", "jpg", "jpeg", "bmp", "tiff"],
#         accept_multiple_files=False,
#         label_visibility="collapsed"
#     )
    
#     if uploaded_file:
#         image = Image.open(uploaded_file).convert("RGB")
#         st.image(image, use_container_width=True, caption=uploaded_file.name)
    
#     with st.expander(t["advanced_options"]):
#         confidence_threshold = st.slider(
#             t["confidence_threshold"],
#             min_value=0.50,
#             max_value=0.99,
#             value=0.85,
#             step=0.01
#         )
#         use_tta = st.toggle(t["tta"], value=False)
    
#     with st.expander(t["patient_info"]):
#         patient_name = st.text_input(t["patient_name"], "")
#         patient_id = st.text_input(t["patient_id"], "")
    
#     run_disabled = uploaded_file is None
#     if st.button(t["run_diagnosis"], type="primary", use_container_width=True, disabled=run_disabled):
#         if uploaded_file is None:
#             st.error(t["error_no_image"])
#         else:
#             with st.spinner(t["processing"]):
#                 try:
#                     result = engine.predict(image)
                    
#                     import tempfile
#                     import os
                    
#                     temp_dir = tempfile.gettempdir()
#                     gradcam_path = os.path.join(temp_dir, f"gradcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    
#                     gradcam_result = engine._generate_gradcam(image, target_class=None, output_path=gradcam_path)
                    
#                     if gradcam_result and os.path.exists(gradcam_path):
#                         gradcam_img = np.array(Image.open(gradcam_path).convert("RGB"))
#                     else:
#                         gradcam_img = np.array(image)
                    
#                     st.session_state.last_result = result
#                     st.session_state.gradcam_img = gradcam_img
#                     st.session_state.patient_name = patient_name
#                     st.session_state.patient_id = patient_id
                    
#                 except Exception as e:
#                     st.error(f"{t['error_processing']}{str(e)}")
    
#     st.markdown('</div>', unsafe_allow_html=True)

# # ─── عرض النتائج أسفل البطاقة في نفس العمود الموسّط ───
# if "last_result" in st.session_state:
#     # إعادة استخدام نفس التخطيط الموسّط للنتائج
#     left_spacer2, col_output, right_spacer2 = st.columns([0.3, 3.4, 0.3])
    
#     with left_spacer2:
#         st.empty()
#     with right_spacer2:
#         st.empty()
    
#     with col_output:
#         result = st.session_state.last_result
#         gradcam_img = st.session_state.gradcam_img
        
#         st.markdown(f'<div class="section-title">{t["results"]}</div>', unsafe_allow_html=True)
        
#         # ← إصلاح: التعامل مع ERROR
#         if result.predicted_class == "ERROR":
#             st.markdown(f"""
#             <div class="diagnosis-box warning">
#                 <h2 style="margin: 0; font-size: 2.5rem;">❌ ERROR</h2>
#                 <p style="font-size: 1.3rem; margin: 10px 0 0;">Model failed to load</p>
#                 <p style="font-size: 1rem; opacity: 0.9; margin: 5px 0 0;">Please check the model file</p>
#             </div>
#             """, unsafe_allow_html=True)
#             st.stop()
        
#         status, icon = get_status_indicator(result.confidence, confidence_threshold)
        
#         if status == "high":
#             box_class = "diagnosis-box"
#         elif status == "review":
#             box_class = "diagnosis-box caution"
#         else:
#             box_class = "diagnosis-box warning"
        
#         predicted_label = result.predicted_class
#         if st.session_state.lang == "ar" and 'CLASS_NAMES_AR' in globals():
#             predicted_label = CLASS_NAMES_AR.get(result.predicted_class, result.predicted_class)
        
#         status_text = get_status_text(status, st.session_state.lang)
        
#         st.markdown(f"""
#         <div class="{box_class}">
#             <h2 style="margin: 0; font-size: 2.5rem;">{icon} {predicted_label}</h2>
#             <p style="font-size: 1.3rem; margin: 10px 0 0;">{t["confidence"]}: {result.confidence:.2%}</p>
#             <p style="font-size: 1rem; opacity: 0.9; margin: 5px 0 0;">{t["status"]}: {status_text}</p>
#         </div>
#         """, unsafe_allow_html=True)
        
#         fig_gauge = go.Figure(data=[go.Indicator(
#             mode="gauge+number",
#             value=result.confidence * 100,
#             number={"suffix": "%", "font": {"size": 36, "color": "#e94560"}},
#             title={"text": t["confidence"], "font": {"size": 14, "color": "white"}},
#             gauge={
#                 "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
#                 "bar": {"color": "#e94560", "thickness": 0.75},
#                 "bgcolor": "rgba(0,0,0,0.3)",
#                 "borderwidth": 2,
#                 "bordercolor": "rgba(255,255,255,0.2)",
#                 "steps": [
#                     {"range": [0, 70], "color": "rgba(255,0,0,0.2)"},
#                     {"range": [70, 85], "color": "rgba(255,193,7,0.2)"},
#                     {"range": [85, 100], "color": "rgba(0,255,0,0.2)"}
#                 ],
#                 "threshold": {
#                     "line": {"color": "red", "width": 3},
#                     "thickness": 0.8,
#                     "value": 85
#                 }
#             }
#         )])
#         fig_gauge.update_layout(
#             height=250,
#             margin=dict(l=20, r=20, t=50, b=20),
#             paper_bgcolor="rgba(0,0,0,0)",
#             font={"color": "white"}
#         )
#         st.plotly_chart(fig_gauge, use_container_width=True, key="gauge")
        
#         st.markdown(f'<div class="section-title">{t["gradcam_title"]}</div>', unsafe_allow_html=True)
#         st.markdown(f'<p style="color: rgba(255,255,255,0.7); font-size: 0.9rem;">{t["gradcam_desc"]}</p>', unsafe_allow_html=True)
#         st.image(gradcam_img, use_container_width=True)
        
#         st.markdown(f'<div class="section-title">{t["probabilities"]}</div>', unsafe_allow_html=True)
        
#         probs = result.probabilities
#         classes = list(probs.keys())
#         values = list(probs.values())
#         colors = ["#e94560" if v == max(values) else "rgba(255,255,255,0.3)" for v in values]
#         labels = [CLASS_NAMES_AR.get(c, c) if st.session_state.lang == "ar" and 'CLASS_NAMES_AR' in globals() else c for c in classes]
        
#         fig_bar = go.Figure(data=[go.Bar(
#             x=values,
#             y=labels,
#             orientation="h",
#             marker_color=colors,
#             text=[f"{v:.1%}" for v in values],
#             textposition="outside",
#             textfont={"color": "white", "size": 12}
#         )])
#         fig_bar.update_layout(
#             title={"text": t["probabilities"], "font": {"color": "white", "size": 16}},
#             xaxis={"title": "Probability" if st.session_state.lang == "en" else "الاحتمال", 
#                    "range": [0, 1.05], "tickformat": ".0%", "color": "white"},
#             yaxis={"color": "white"},
#             plot_bgcolor="rgba(0,0,0,0)",
#             paper_bgcolor="rgba(0,0,0,0)",
#             height=300,
#             margin=dict(l=120, r=30, t=50, b=40),
#             showlegend=False
#         )
#         st.plotly_chart(fig_bar, use_container_width=True, key="prob")
        
#         st.markdown(f'<div class="section-title">{t["clinical_report"]}</div>', unsafe_allow_html=True)
        
#         descriptions = {
#             "en": {
#                 "Basophil": "Granulocyte with large dark granules. Involved in allergic reactions.",
#                 "Eosinophil": "Granulocyte with red-orange granules. Key in parasitic defense.",
#                 "Lymphocyte": "Agranulocyte with large nucleus. Central to adaptive immunity.",
#                 "Monocyte": "Largest WBC with kidney-shaped nucleus. Precursor to macrophages.",
#                 "Neutrophil": "Most abundant granulocyte. Primary defense against bacteria."
#             },
#             "ar": {
#                 "Basophil": "خلية حبيبية ذات حبيبات داكنة كبيرة. تشارك في ردود الفعل التحسسية.",
#                 "Eosinophil": "خلية حبيبية ذات حبيبات برتقالية حمراء. دور رئيسي في الدفاع الطفيلي.",
#                 "Lymphocyte": "خلية غير حبيبية ذات نواة كبيرة. محور المناعة التكيفية.",
#                 "Monocyte": "أكبر خلايا الدم البيضاء ذات نواة على شكل كلية. سلف البلعميات.",
#                 "Neutrophil": "أكثر الخلايا الحبيبية شيوعاً. الدفاع الأول ضد البكتيريا."
#             }
#         }
        
#         # ← إصلاح: التحقق من وجود الفئة في الوصف
#         if result.predicted_class in descriptions[st.session_state.lang]:
#             desc = descriptions[st.session_state.lang][result.predicted_class]
#         else:
#             desc = "No description available."
#         st.info(desc)
        
#         ranges = {
#             "Basophil": "0.5% - 1.0%",
#             "Eosinophil": "1.0% - 4.0%",
#             "Lymphocyte": "20.0% - 40.0%",
#             "Monocyte": "2.0% - 8.0%",
#             "Neutrophil": "40.0% - 70.0%"
#         }
        
#         if result.predicted_class in ranges:
#             st.markdown(f"**{t['normal_range']}:** `{ranges[result.predicted_class]}`")
        
#         recs = {
#             "en": {
#                 "Basophil": ["Monitor allergic conditions", "Check inflammation markers"],
#                 "Eosinophil": ["Investigate parasitic infections", "Assess allergic status"],
#                 "Lymphocyte": ["Evaluate immune status", "Consider viral panel"],
#                 "Monocyte": ["Monitor chronic infections", "Check inflammatory markers"],
#                 "Neutrophil": ["Check bacterial infection", "Monitor inflammatory response"]
#             },
#             "ar": {
#                 "Basophil": ["مراقبة الحالات التحسسية", "فحص مؤشرات الالتهاب"],
#                 "Eosinophil": ["التحقيق في العدوى الطفيلية", "تقييم الحالة التحسسية"],
#                 "Lymphocyte": ["تقييم الحالة المناعية", "النظر في لوحة الفيروسات"],
#                 "Monocyte": ["مراقبة العدوى المزمنة", "فحص مؤشرات الالتهاب"],
#                 "Neutrophil": ["التحقق من العدوى البكتيرية", "مراقبة الاستجابة الالتهابية"]
#             }
#         }
        
#         if result.predicted_class in recs[st.session_state.lang]:
#             st.markdown(f"**{t['recommendations']}:**")
#             for rec in recs[st.session_state.lang][result.predicted_class]:
#                 st.markdown(f"- {rec}")
        
#         st.markdown("---")
#         try:
#             reporter = ReportGenerator(lang=st.session_state.lang)
#             result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else result
#             report_html = reporter.generate_html(
#                 result=result_dict,
#                 patient_name=st.session_state.get("patient_name", ""),
#                 patient_id=st.session_state.get("patient_id", "")
#             )
            
#             with open(report_html, "r", encoding="utf-8") as f:
#                 report_content = f.read()
            
#             st.download_button(
#                 label=t["download_report"],
#                 data=report_content,
#                 file_name=f"WBC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
#                 mime="text/html",
#                 use_container_width=True
#             )
#         except Exception as e:
#             st.warning(f"Could not generate report: {e}")




"""
WBC Vision AI - Single Diagnosis Page (Centered & Organized Layout)
"""

import streamlit as st
import numpy as np
from PIL import Image
from pathlib import Path
import plotly.graph_objects as go
from datetime import datetime
from dataclasses import asdict

st.set_page_config(
    page_title="Single Diagnosis | Al-Shameeri AI Vision",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

import sys
sys.path.append(str(Path(__file__).parent.parent))

from config import *
from engine import WBCInferenceEngine
from utils import get_status_indicator, get_status_text
from reporter import ReportGenerator

if "lang" not in st.session_state:
    st.session_state.lang = "en"

TEXTS = {
    "en": {
        "title": "🔬 Single Cell Diagnosis",
        "subtitle": "Upload a blood smear image for instant AI analysis",
        "upload_title": "📤 Upload Image",
        "upload_help": "Supported formats: PNG, JPG, JPEG, BMP, TIFF",
        "advanced_options": "⚙️ Advanced Options",
        "confidence_threshold": "Confidence Threshold",
        "tta": "Test-Time Augmentation (TTA)",
        "run_diagnosis": "🚀 Run AI Diagnosis",
        "processing": "🔍 Analyzing image...",
        "results": "📊 Diagnosis Results",
        "predicted_class": "Predicted Class",
        "confidence": "Confidence",
        "status": "Status",
        "gradcam_title": "🎯 Grad-CAM Analysis",
        "gradcam_desc": "Heatmap shows regions the AI focused on",
        "probabilities": "📈 Probability Distribution",
        "clinical_report": "📝 Clinical Report",
        "description": "Description",
        "normal_range": "Normal Range",
        "recommendations": "Recommendations",
        "download_report": "📄 Download Medical Report",
        "patient_info": "👤 Patient Information (Optional)",
        "patient_name": "Patient Name",
        "patient_id": "Patient ID",
        "back_home": "← Back to Home",
        "medical_disclaimer": "⚠️ This is an AI-assisted tool. Final diagnosis requires expert review.",
        "error_no_image": "❌ Please upload an image first",
        "error_processing": "❌ Error processing image: ",
    },
    "ar": {
        "title": "🔬 التشخيص الفردي",
        "subtitle": "ارفع صورة مسحة دم للتحليل الفوري بالذكاء الاصطناعي",
        "upload_title": "📤 رفع الصورة",
        "upload_help": "الصيغ المدعومة: PNG, JPG, JPEG, BMP, TIFF",
        "advanced_options": "⚙️ خيارات متقدمة",
        "confidence_threshold": "عتبة الثقة",
        "tta": "تعزيز وقت الاختبار (TTA)",
        "run_diagnosis": "🚀 تشغيل التشخيص الذكي",
        "processing": "🔍 جاري تحليل الصورة...",
        "results": "📊 نتائج التشخيص",
        "predicted_class": "الفئة المتوقعة",
        "confidence": "نسبة الثقة",
        "status": "الحالة",
        "gradcam_title": "🎯 تحليل Grad-CAM",
        "gradcam_desc": "الخريطة الحرارية تظهر المناطق التي ركز عليها الذكاء الاصطناعي",
        "probabilities": "📈 توزيع الاحتمالات",
        "clinical_report": "📝 التقرير السريري",
        "description": "الوصف",
        "normal_range": "النطاق الطبيعي",
        "recommendations": "التوصيات",
        "download_report": "📄 تحميل التقرير الطبي",
        "patient_info": "👤 معلومات المريض (اختياري)",
        "patient_name": "اسم المريض",
        "patient_id": "رقم المريض",
        "back_home": "← العودة للرئيسية",
        "medical_disclaimer": "⚠️ هذه أداة مساعدة بالذكاء الاصطناعي. التشخيص النهائي يتطلب مراجعة خبير.",
        "error_no_image": "❌ الرجاء رفع صورة أولاً",
        "error_processing": "❌ خطأ في معالجة الصورة: ",
    }
}

t = TEXTS[st.session_state.lang]

st.markdown("""
<style>
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        background-attachment: fixed;
    }
    .main .block-container {
        max-width: 1400px;
        padding: 2rem 3rem;
    }
    /* ─── بطاقة التشخيص الرئيسية ─── */
    .diagnosis-box {
        background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);
        padding: 40px;
        border-radius: 24px;
        color: white;
        text-align: center;
        box-shadow: 0 20px 40px rgba(17, 153, 142, 0.3);
        margin: 20px 0;
    }
    .diagnosis-box.warning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        box-shadow: 0 20px 40px rgba(245, 87, 108, 0.3);
    }
    .diagnosis-box.caution {
        background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);
        box-shadow: 0 20px 40px rgba(250, 112, 154, 0.3);
    }
    /* ─── عناوين الأقسام ─── */
    .section-title {
        color: #e94560;
        font-size: 1.5rem;
        font-weight: 700;
        margin: 35px 0 20px;
        padding-bottom: 12px;
        border-bottom: 2px solid rgba(233, 69, 96, 0.3);
    }
    .section-title:first-of-type {
        margin-top: 10px;
    }
    /* ─── البانر الطبي ─── */
    .medical-banner {
        background: linear-gradient(90deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
        border: 1px solid rgba(255, 193, 7, 0.5);
        border-radius: 16px;
        padding: 12px 20px;
        text-align: center;
        color: #ffc107;
        font-size: 0.85rem;
        margin-bottom: 20px;
    }
    /* ─── بطاقة الإدخال (الوسط) ─── */
    .input-card {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 24px;
        padding: 40px;
        backdrop-filter: blur(10px);
        box-shadow: 0 8px 32px rgba(0, 0, 0, 0.2);
    }
    .input-card:hover {
        border-color: rgba(233, 69, 96, 0.3);
        box-shadow: 0 8px 32px rgba(233, 69, 96, 0.1);
        transition: all 0.3s ease;
    }
    /* ─── بطاقات النتائج المنفصلة ─── */
    .result-card {
        background: rgba(255, 255, 255, 0.02);
        border: 1px solid rgba(255, 255, 255, 0.06);
        border-radius: 20px;
        padding: 30px;
        margin: 20px 0;
        backdrop-filter: blur(5px);
    }
    .result-card:hover {
        border-color: rgba(233, 69, 96, 0.2);
        transition: all 0.3s ease;
    }
    /* ─── تنسيق زر الرجوع ─── */
    .back-btn-container {
        text-align: center;
        margin-bottom: 20px;
    }
    /* ─── تنسيق رافع الملفات ─── */
    div[data-testid="stFileUploader"] > section {
        background: rgba(0, 0, 0, 0.2);
        border: 2px dashed rgba(233, 69, 96, 0.4);
        border-radius: 16px;
        padding: 30px;
    }
    div[data-testid="stFileUploader"] > section:hover {
        border-color: #e94560;
        background: rgba(233, 69, 96, 0.05);
    }
    /* ─── تنسيق expander ─── */
    details {
        background: rgba(0, 0, 0, 0.2) !important;
        border: 1px solid rgba(255, 255, 255, 0.1) !important;
        border-radius: 12px !important;
        margin: 10px 0 !important;
    }
    /* ─── تنسيق الأزرار ─── */
    .stButton > button {
        border-radius: 12px;
        font-weight: 600;
        height: 3rem;
        transition: all 0.3s ease;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #e94560 0%, #ff6b6b 100%);
        border: none;
        box-shadow: 0 4px 15px rgba(233, 69, 96, 0.4);
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(233, 69, 96, 0.6);
    }
    /* ─── فاصل بين الأقسام ─── */
    .section-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(233, 69, 96, 0.3), transparent);
        margin: 30px 0;
    }
    /* ─── تنسيق Grad-CAM ─── */
    .gradcam-container {
        text-align: center;
        padding: 20px;
    }
    .gradcam-container img {
        border-radius: 16px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
    }
    /* ─── تنسيق التقرير السريري ─── */
    .clinical-card {
        background: rgba(0, 0, 0, 0.15);
        border-radius: 16px;
        padding: 25px;
        border-left: 4px solid #e94560;
    }
</style>
""", unsafe_allow_html=True)

st.markdown(f'<div class="medical-banner">{t["medical_disclaimer"]}</div>', unsafe_allow_html=True)
st.markdown(f'<h1 style="color: white; text-align: center; font-size: 2.5rem; font-weight: 800;">{t["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p style="color: rgba(255,255,255,0.7); text-align: center; font-size: 1.1rem; margin-bottom: 30px;">{t["subtitle"]}</p>', unsafe_allow_html=True)

# ─── زر الرجوع في المنتصف ───
st.markdown('<div class="back-btn-container">', unsafe_allow_html=True)
if st.button(t["back_home"], key="back_home"):
    st.switch_page("app.py")
st.markdown('</div>', unsafe_allow_html=True)

@st.cache_resource(show_spinner=False)
def load_model():
    return WBCInferenceEngine()

try:
    engine = load_model()
except Exception as e:
    st.error(f"❌ Error loading model: {str(e)}")
    st.stop()

# ═══════════════════════════════════════════════════════
# ║  القسم الأول: عمود الإدخال في المنتصف                ║
# ═══════════════════════════════════════════════════════
left_spacer, col_input, right_spacer = st.columns([1, 2.2, 1])

with left_spacer:
    st.empty()

with right_spacer:
    st.empty()

with col_input:
    st.markdown('<div class="input-card">', unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-title" style="margin-top: 0;">{t["upload_title"]}</div>', unsafe_allow_html=True)
    
    uploaded_file = st.file_uploader(
        t["upload_help"],
        type=["png", "jpg", "jpeg", "bmp", "tiff"],
        accept_multiple_files=False,
        label_visibility="collapsed"
    )
    
    if uploaded_file:
        image = Image.open(uploaded_file).convert("RGB")
        st.image(image, use_container_width=True, caption=uploaded_file.name)
    
    with st.expander(t["advanced_options"]):
        confidence_threshold = st.slider(
            t["confidence_threshold"],
            min_value=0.50,
            max_value=0.99,
            value=0.85,
            step=0.01
        )
        use_tta = st.toggle(t["tta"], value=False)
    
    with st.expander(t["patient_info"]):
        patient_name = st.text_input(t["patient_name"], "")
        patient_id = st.text_input(t["patient_id"], "")
    
    run_disabled = uploaded_file is None
    if st.button(t["run_diagnosis"], type="primary", use_container_width=True, disabled=run_disabled):
        if uploaded_file is None:
            st.error(t["error_no_image"])
        else:
            with st.spinner(t["processing"]):
                try:
                    result = engine.predict(image)
                    
                    import tempfile
                    import os
                    
                    temp_dir = tempfile.gettempdir()
                    gradcam_path = os.path.join(temp_dir, f"gradcam_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png")
                    
                    gradcam_result = engine._generate_gradcam(image, target_class=None, output_path=gradcam_path)
                    
                    if gradcam_result and os.path.exists(gradcam_path):
                        gradcam_img = np.array(Image.open(gradcam_path).convert("RGB"))
                    else:
                        gradcam_img = np.array(image)
                    
                    st.session_state.last_result = result
                    st.session_state.gradcam_img = gradcam_img
                    st.session_state.patient_name = patient_name
                    st.session_state.patient_id = patient_id
                    
                except Exception as e:
                    st.error(f"{t['error_processing']}{str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# ═══════════════════════════════════════════════════════
# ║  القسم الثاني: النتائج — كل قسم في صف منفصل         ║
# ═══════════════════════════════════════════════════════
if "last_result" in st.session_state:
    result = st.session_state.last_result
    gradcam_img = st.session_state.gradcam_img
    
    # ─── فاصل بصري ───
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 1️⃣ بطاقة التشخيص الرئيسية (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown(f'<div class="section-title">{t["results"]}</div>', unsafe_allow_html=True)
    
    if result.predicted_class == "ERROR":
        st.markdown(f"""
        <div class="diagnosis-box warning">
            <h2 style="margin: 0; font-size: 2.5rem;">❌ ERROR</h2>
            <p style="font-size: 1.3rem; margin: 10px 0 0;">Model failed to load</p>
            <p style="font-size: 1rem; opacity: 0.9; margin: 5px 0 0;">Please check the model file</p>
        </div>
        """, unsafe_allow_html=True)
        st.stop()
    
    status, icon = get_status_indicator(result.confidence, confidence_threshold)
    
    if status == "high":
        box_class = "diagnosis-box"
    elif status == "review":
        box_class = "diagnosis-box caution"
    else:
        box_class = "diagnosis-box warning"
    
    predicted_label = result.predicted_class
    if st.session_state.lang == "ar" and 'CLASS_NAMES_AR' in globals():
        predicted_label = CLASS_NAMES_AR.get(result.predicted_class, result.predicted_class)
    
    status_text = get_status_text(status, st.session_state.lang)
    
    st.markdown(f"""
    <div class="{box_class}">
        <h2 style="margin: 0; font-size: 2.5rem;">{icon} {predicted_label}</h2>
        <p style="font-size: 1.3rem; margin: 10px 0 0;">{t["confidence"]}: {result.confidence:.2%}</p>
        <p style="font-size: 1rem; opacity: 0.9; margin: 5px 0 0;">{t["status"]}: {status_text}</p>
    </div>
    """, unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 2️⃣ Confidence Gauge (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">📊 {t["confidence"]}</div>', unsafe_allow_html=True)
    
    fig_gauge = go.Figure(data=[go.Indicator(
        mode="gauge+number",
        value=result.confidence * 100,
        number={"suffix": "%", "font": {"size": 36, "color": "#e94560"}},
        title={"text": t["confidence"], "font": {"size": 14, "color": "white"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "white"},
            "bar": {"color": "#e94560", "thickness": 0.75},
            "bgcolor": "rgba(0,0,0,0.3)",
            "borderwidth": 2,
            "bordercolor": "rgba(255,255,255,0.2)",
            "steps": [
                {"range": [0, 70], "color": "rgba(255,0,0,0.2)"},
                {"range": [70, 85], "color": "rgba(255,193,7,0.2)"},
                {"range": [85, 100], "color": "rgba(0,255,0,0.2)"}
            ],
            "threshold": {
                "line": {"color": "red", "width": 3},
                "thickness": 0.8,
                "value": 85
            }
        }
    )])
    fig_gauge.update_layout(
        height=280,
        margin=dict(l=20, r=20, t=50, b=20),
        paper_bgcolor="rgba(0,0,0,0)",
        font={"color": "white"}
    )
    st.plotly_chart(fig_gauge, use_container_width=True, key="gauge")
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 3️⃣ Grad-CAM Analysis (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{t["gradcam_title"]}</div>', unsafe_allow_html=True)
    st.markdown(f'<p style="color: rgba(255,255,255,0.7); font-size: 0.9rem; margin-bottom: 20px;">{t["gradcam_desc"]}</p>', unsafe_allow_html=True)
    
    st.markdown('<div class="result-card gradcam-container">', unsafe_allow_html=True)
    st.image(gradcam_img, use_container_width=True)
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 4️⃣ Probability Distribution (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{t["probabilities"]}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="result-card">', unsafe_allow_html=True)
    
    probs = result.probabilities
    classes = list(probs.keys())
    values = list(probs.values())
    colors = ["#e94560" if v == max(values) else "rgba(255,255,255,0.3)" for v in values]
    labels = [CLASS_NAMES_AR.get(c, c) if st.session_state.lang == "ar" and 'CLASS_NAMES_AR' in globals() else c for c in classes]
    
    fig_bar = go.Figure(data=[go.Bar(
        x=values,
        y=labels,
        orientation="h",
        marker_color=colors,
        text=[f"{v:.1%}" for v in values],
        textposition="outside",
        textfont={"color": "white", "size": 12}
    )])
    fig_bar.update_layout(
        title={"text": t["probabilities"], "font": {"color": "white", "size": 16}},
        xaxis={"title": "Probability" if st.session_state.lang == "en" else "الاحتمال", 
               "range": [0, 1.05], "tickformat": ".0%", "color": "white"},
        yaxis={"color": "white"},
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        height=350,
        margin=dict(l=120, r=30, t=50, b=40),
        showlegend=False
    )
    st.plotly_chart(fig_bar, use_container_width=True, key="prob")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 5️⃣ Clinical Report (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    st.markdown(f'<div class="section-title">{t["clinical_report"]}</div>', unsafe_allow_html=True)
    
    st.markdown('<div class="result-card clinical-card">', unsafe_allow_html=True)
    
    descriptions = {
        "en": {
            "Basophil": "Granulocyte with large dark granules. Involved in allergic reactions.",
            "Eosinophil": "Granulocyte with red-orange granules. Key in parasitic defense.",
            "Lymphocyte": "Agranulocyte with large nucleus. Central to adaptive immunity.",
            "Monocyte": "Largest WBC with kidney-shaped nucleus. Precursor to macrophages.",
            "Neutrophil": "Most abundant granulocyte. Primary defense against bacteria."
        },
        "ar": {
            "Basophil": "خلية حبيبية ذات حبيبات داكنة كبيرة. تشارك في ردود الفعل التحسسية.",
            "Eosinophil": "خلية حبيبية ذات حبيبات برتقالية حمراء. دور رئيسي في الدفاع الطفيلي.",
            "Lymphocyte": "خلية غير حبيبية ذات نواة كبيرة. محور المناعة التكيفية.",
            "Monocyte": "أكبر خلايا الدم البيضاء ذات نواة على شكل كلية. سلف البلعميات.",
            "Neutrophil": "أكثر الخلايا الحبيبية شيوعاً. الدفاع الأول ضد البكتيريا."
        }
    }
    
    if result.predicted_class in descriptions[st.session_state.lang]:
        desc = descriptions[st.session_state.lang][result.predicted_class]
    else:
        desc = "No description available."
    st.info(desc)
    
    ranges = {
        "Basophil": "0.5% - 1.0%",
        "Eosinophil": "1.0% - 4.0%",
        "Lymphocyte": "20.0% - 40.0%",
        "Monocyte": "2.0% - 8.0%",
        "Neutrophil": "40.0% - 70.0%"
    }
    
    if result.predicted_class in ranges:
        st.markdown(f"**{t['normal_range']}:** `{ranges[result.predicted_class]}`")
    
    recs = {
        "en": {
            "Basophil": ["Monitor allergic conditions", "Check inflammation markers"],
            "Eosinophil": ["Investigate parasitic infections", "Assess allergic status"],
            "Lymphocyte": ["Evaluate immune status", "Consider viral panel"],
            "Monocyte": ["Monitor chronic infections", "Check inflammatory markers"],
            "Neutrophil": ["Check bacterial infection", "Monitor inflammatory response"]
        },
        "ar": {
            "Basophil": ["مراقبة الحالات التحسسية", "فحص مؤشرات الالتهاب"],
            "Eosinophil": ["التحقيق في العدوى الطفيلية", "تقييم الحالة التحسسية"],
            "Lymphocyte": ["تقييم الحالة المناعية", "النظر في لوحة الفيروسات"],
            "Monocyte": ["مراقبة العدوى المزمنة", "فحص مؤشرات الالتهاب"],
            "Neutrophil": ["التحقق من العدوى البكتيرية", "مراقبة الاستجابة الالتهابية"]
        }
    }
    
    if result.predicted_class in recs[st.session_state.lang]:
        st.markdown(f"**{t['recommendations']}:**")
        for rec in recs[st.session_state.lang][result.predicted_class]:
            st.markdown(f"- {rec}")
    
    st.markdown('</div>', unsafe_allow_html=True)
    
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    # 6️⃣ Download Report (Full Width)
    # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
    st.markdown('<hr class="section-divider">', unsafe_allow_html=True)
    
    try:
        reporter = ReportGenerator(lang=st.session_state.lang)
        result_dict = asdict(result) if hasattr(result, '__dataclass_fields__') else result
        report_html = reporter.generate_html(
            result=result_dict,
            patient_name=st.session_state.get("patient_name", ""),
            patient_id=st.session_state.get("patient_id", "")
        )
        
        with open(report_html, "r", encoding="utf-8") as f:
            report_content = f.read()
        
        st.download_button(
            label=t["download_report"],
            data=report_content,
            file_name=f"WBC_Report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html",
            mime="text/html",
            use_container_width=True
        )
    except Exception as e:
        st.warning(f"Could not generate report: {e}")