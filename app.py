
"""
WBC Vision AI - Main Application
Al-Shameeri AI Vision - Stunning Home Page
"""

import streamlit as st
from pathlib import Path
import time

# ==================== PAGE CONFIG ====================
st.set_page_config(
    page_title="Al-Shameeri AI Vision | WBC Diagnostic System",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ==================== CUSTOM CSS (محسّن) ====================
st.markdown("""
<style>
    /* إخفاء العناصر الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* الخلفية المتحركة (خفيفة) */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
        background-attachment: fixed;
    }
    
    /* البطاقات الزجاجية (غير قابلة للنقر) */
    .glass-card {
        background: rgba(255, 255, 255, 0.08);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255, 255, 255, 0.15);
        border-radius: 24px;
        padding: 40px 30px;
        color: white;
        text-align: center;
        transition: all 0.4s ease;
        height: 100%;
    }
    
    .glass-card:hover {
        transform: translateY(-10px);
        background: rgba(255, 255, 255, 0.15);
        box-shadow: 0 25px 50px rgba(0, 0, 0, 0.4);
    }
    
    .glass-card .icon {
        font-size: 3.5rem;
        margin-bottom: 20px;
        display: block;
    }
    
    .glass-card h3 {
        font-size: 1.6rem;
        font-weight: 700;
        margin-bottom: 12px;
        color: #fff;
    }
    
    .glass-card p {
        font-size: 0.95rem;
        opacity: 0.85;
        line-height: 1.6;
        margin-bottom: 25px;
    }
    
    /* العنوان الرئيسي */
    .hero-title {
        font-size: 3.5rem;
        font-weight: 800;
        color: white;
        text-align: center;
        text-shadow: 0 4px 30px rgba(0, 0, 0, 0.5);
        margin-bottom: 5px;
        letter-spacing: -1px;
    }
    
    .hero-subtitle {
        font-size: 1.2rem;
        color: rgba(255, 255, 255, 0.8);
        text-align: center;
        margin-bottom: 10px;
        font-weight: 300;
    }
    
    .hero-brand {
        font-size: 1rem;
        color: #4a90d9;
        text-align: center;
        font-weight: 600;
        letter-spacing: 3px;
        text-transform: uppercase;
        margin-bottom: 40px;
    }
    
    /* شريط التنقل العلوي */
    .nav-bar {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 15px 30px;
        background: rgba(0, 0, 0, 0.3);
        backdrop-filter: blur(15px);
        border-radius: 16px;
        margin-bottom: 30px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    
    .nav-logo {
        font-size: 1.4rem;
        font-weight: 700;
        color: white;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    
    /* زر اللغة */
    .lang-btn {
        background: rgba(74, 144, 217, 0.2);
        border: 1px solid rgba(74, 144, 217, 0.5);
        color: #4a90d9;
        padding: 8px 20px;
        border-radius: 25px;
        cursor: pointer;
        transition: all 0.3s;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .lang-btn:hover {
        background: rgba(74, 144, 217, 0.4);
        transform: scale(1.05);
    }
    
    /* الإحصائيات */
    .stats-grid {
        display: flex;
        justify-content: center;
        gap: 25px;
        margin-top: 50px;
        flex-wrap: wrap;
    }
    
    .stat-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 20px;
        padding: 25px 30px;
        text-align: center;
        color: white;
        min-width: 150px;
    }
    
    .stat-box .number {
        font-size: 2.2rem;
        font-weight: 800;
        color: #4a90d9;
        display: block;
    }
    
    .stat-box .label {
        font-size: 0.85rem;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* حالة النظام */
    .status-bar {
        display: flex;
        justify-content: center;
        gap: 20px;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    
    .status-item {
        display: flex;
        align-items: center;
        gap: 8px;
        background: rgba(0, 0, 0, 0.3);
        padding: 10px 20px;
        border-radius: 30px;
        color: rgba(255, 255, 255, 0.9);
        font-size: 0.9rem;
    }
    
    .status-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background: #28a745;
        animation: pulse 2s infinite;
    }
    
    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    /* تنبيه طبي */
    .medical-banner {
        background: linear-gradient(90deg, rgba(255, 193, 7, 0.2), rgba(255, 152, 0, 0.2));
        border: 1px solid rgba(255, 193, 7, 0.5);
        border-radius: 16px;
        padding: 15px 25px;
        text-align: center;
        color: #ffc107;
        font-size: 0.9rem;
        margin-bottom: 30px;
        display: flex;
        align-items: center;
        justify-content: center;
        gap: 10px;
    }
    
    /* زر التنقل */
    .nav-button {
        background: linear-gradient(135deg, #2c5a8a 0%, #4a7fb5 100%);
        color: white;
        border: none;
        padding: 12px 30px;
        border-radius: 30px;
        font-weight: 600;
        cursor: pointer;
        transition: all 0.3s;
        width: 100%;
        font-size: 1rem;
    }
    
    .nav-button:hover {
        transform: scale(1.05);
        box-shadow: 0 10px 30px rgba(44, 90, 138, 0.4);
    }
    
    /* الفوتر */
    .footer-text {
        text-align: center;
        color: rgba(255, 255, 255, 0.5);
        padding: 30px;
        font-size: 0.85rem;
    }
    
    /* صورة الواجهة */
    .hero-image-container {
        text-align: center;
        margin: 20px 0 40px 0;
    }
    
    .hero-image {
        max-width: 500px;
        width: 100%;
        height: auto;
        border-radius: 20px;
        opacity: 0.9;
        box-shadow: 0 15px 50px rgba(0, 0, 0, 0.5);
        transition: all 0.4s ease;
    }
    
    .hero-image:hover {
        transform: scale(1.02);
        opacity: 1;
        box-shadow: 0 20px 60px rgba(74, 144, 217, 0.2);
    }
    
    /* قسم قواعد البيانات */
    .dataset-section {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        margin: 40px 0;
        text-align: center;
    }
    
    .dataset-title {
        color: #4a90d9;
        font-size: 1.3rem;
        font-weight: 700;
        margin-bottom: 20px;
    }
    
    .dataset-grid {
        display: flex;
        justify-content: center;
        gap: 20px;
        flex-wrap: wrap;
    }
    
    .dataset-box {
        background: rgba(255, 255, 255, 0.05);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px 25px;
        text-align: center;
        color: white;
        min-width: 140px;
    }
    
    .dataset-box .number {
        font-size: 1.8rem;
        font-weight: 800;
        color: #4a90d9;
        display: block;
    }
    
    .dataset-box .label {
        font-size: 0.8rem;
        opacity: 0.8;
        margin-top: 5px;
    }
    
    /* معلومات الاتصال */
    .contact-bar {
        display: flex;
        justify-content: center;
        gap: 30px;
        margin: 30px 0;
        flex-wrap: wrap;
    }
    
    .contact-item {
        display: flex;
        align-items: center;
        gap: 10px;
        color: rgba(255, 255, 255, 0.7);
        font-size: 0.9rem;
        text-decoration: none;
        transition: all 0.3s;
    }
    
    .contact-item:hover {
        color: #4a90d9;
        transform: translateY(-2px);
    }
    
    /* القائمة المنسدلة */
    .info-dropdown {
        background: rgba(0, 0, 0, 0.4);
        border: 1px solid rgba(255, 255, 255, 0.1);
        border-radius: 16px;
        padding: 20px;
        margin: 20px 0;
        color: white;
    }
    
    .info-dropdown h4 {
        color: #4a90d9;
        margin-bottom: 10px;
    }
    
    .info-dropdown p {
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.6;
        font-size: 0.9rem;
    }
    
    /* قسم ملخص المشروع */
    .project-summary {
        background: rgba(255, 255, 255, 0.03);
        border: 1px solid rgba(255, 255, 255, 0.08);
        border-radius: 20px;
        padding: 30px;
        margin: 30px 0;
        color: white;
    }
    
    .project-summary h3 {
        color: #4a90d9;
        font-size: 1.4rem;
        margin-bottom: 15px;
        text-align: center;
    }
    
    .project-summary p {
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.8;
        font-size: 0.95rem;
        text-align: center;
    }
    
    .project-summary ul {
        color: rgba(255, 255, 255, 0.85);
        line-height: 1.8;
        font-size: 0.9rem;
        padding-left: 20px;
    }
    
    .project-summary li {
        margin-bottom: 8px;
    }
</style>
""", unsafe_allow_html=True)

# ==================== LANGUAGE ====================
if "lang" not in st.session_state:
    st.session_state.lang = "en"

def toggle_lang():
    st.session_state.lang = "ar" if st.session_state.lang == "en" else "en"

# ==================== TEXTS ====================
TEXTS = {
    "en": {
        "brand": "Al-Shameeri AI Vision",
        "title": "WBC Diagnostic System",
        "subtitle": "AI-Powered White Blood Cell Classification",
        "diagnosis_title": "Single Diagnosis",
        "diagnosis_desc": "Upload a blood smear image for instant AI analysis with Grad-CAM visualization",
        "batch_title": "Batch Analysis",
        "batch_desc": "Process multiple images simultaneously with comprehensive reports",
        "dashboard_title": "Analytics Dashboard",
        "dashboard_desc": "View system performance, statistics, and historical data",
        "start_btn": "Start Analysis",
        "batch_btn": "Process Batch",
        "dashboard_btn": "View Dashboard",
        "accuracy": "99.28%",
        "accuracy_label": "Model Accuracy",
        "classes": "5 Classes",
        "classes_label": "WBC Types",
        "speed": "<50ms",
        "speed_label": "Inference Time",
        "samples": "17K+",
        "samples_label": "Training Images",
        "model_ready": "Model Ready",
        "gpu_status": "GPU Active" if st.session_state.get('gpu', False) else "CPU Mode",
        "inference_ready": "Inference Engine Ready",
        "medical_warning": " This tool assists in diagnosis. Final review requires a certified hematologist.",
        "footer": "© 2024 Al-Shameeri AI Vision | Advanced Medical Imaging Solutions",
        "dataset_title": "📊 Dataset & Evaluation",
        "train_set": "Train Set",
        "train_count": "17,000+",
        "test_a": "Test-A",
        "test_a_count": "5,000",
        "test_b": "Test-B",
        "test_b_count": "4,500",
        "total_eval": "Total Eval",
        "total_eval_count": "9,500",
        "about_title": "ℹ️ About",
        "about_developer": "👨‍💻 Developer",
        "about_dev_name": "Eng.Yunes Abdulghani Al-Shameeri",
        "about_project": "📋 Project Summary",
        "about_project_text": "WBC Vision AI is a deep learning-based clinical decision support system (CDSS) for automated classification of white blood cells (WBC) from peripheral blood smear images. The system utilizes EfficientNet-V2-S architecture achieving 99.28% accuracy across 5 WBC classes: Neutrophil, Lymphocyte, Monocyte, Eosinophil, and Basophil.",
        "about_system": "🔬 System Overview",
        "about_system_text": "The system provides real-time AI-assisted diagnosis with Grad-CAM visualization, batch processing capabilities, and comprehensive analytics dashboard. It serves as a hospital-grade tool to assist hematologists in preliminary screening and classification of blood cell disorders.",
        "about_future": "🚀 Future Development",
        "about_future_text": "Planned enhancements include: RBC and platelet detection, complete CBC automation, cloud deployment for multi-hospital access, integration with LIS/HIS systems, and FDA/CE medical device certification pathway.",
        "contact_email": "📧 alshameeri.ai.eng@gmail.com",
        "contact_whatsapp": "📱 +967 773 792 775",
        "menu_about": "About Project",
        "menu_developer": "Developer Info",
        "menu_system": "System Info",
        "project_summary_title": "🧬 Project Overview",
        "project_summary_text": "An advanced Deep Learning-based medical image classification system for automatic recognition of five types of White Blood Cells using state-of-the-art Computer Vision techniques. The model was trained on 17,000+ labeled medical images and evaluated on two completely unseen external datasets (Test-A: 5,000 images, Test-B: 4,500 images), achieving excellent accuracy and strong generalization performance.",
        "model_arch": "🏗️ Architecture",
        "model_arch_text": "EfficientNet-V2-S (Transfer Learning) with PyTorch framework",
        "techniques": "🔧 Techniques",
        "techniques_list": [
            "CrossEntropyLoss with Label Smoothing",
            "AdamW Optimizer with Cosine Annealing LR",
            "Mixed Precision Training (AMP/GradScaler)",
            "Data Augmentation: Rotation, Flip, Color Jitter",
            "Explainable AI: Confusion Matrix, ROC Curve, AUC"
        ],
        "performance": "📈 Performance",
        "performance_list": [
            "Training Accuracy: >99.5%",
            "External Test Accuracy: ~98.99%",
            "Strong generalization on unseen datasets",
            "Detailed classification report and ROC-AUC analysis"
        ],
        "future_work": "🔮 Future Work",
        "future_work_list": [
            "Clinical-ready user interface for medical professionals",
            "Integration into bedside clinical decision support system",
            "Enhanced model reliability and interpretability",
            "Deployment in hospital and laboratory environments"
        ],
    },
    "ar": {
        "brand": "رؤية الشميري الذكية",
        "title": "نظام تشخيص خلايا الدم البيضاء",
        "subtitle": "تصنيف خلايا الدم بالذكاء الاصطناعي",
        "diagnosis_title": "تشخيص فردي",
        "diagnosis_desc": "ارفع صورة مسحة دم للتحليل الفوري مع Grad-CAM",
        "batch_title": "تحليل مجمع",
        "batch_desc": "معالجة عدة صور معاً مع تقارير شاملة",
        "dashboard_title": "لوحة التحليلات",
        "dashboard_desc": "عرض أداء النظام والإحصائيات والبيانات التاريخية",
        "start_btn": "بدء التحليل",
        "batch_btn": "معالجة مجمعة",
        "dashboard_btn": "عرض اللوحة",
        "accuracy": "99.28%",
        "accuracy_label": "دقة النموذج",
        "classes": "5 فئات",
        "classes_label": "أنواع الخلايا",
        "speed": "أقل من 50ملي",
        "speed_label": "وقت الاستنتاج",
        "samples": "17 ألف+",
        "samples_label": "صور التدريب",
        "model_ready": "النموذج جاهز",
        "gpu_status": "GPU نشط" if st.session_state.get('gpu', False) else "وضع CPU",
        "inference_ready": "محرك الاستنتاج جاهز",
        "medical_warning": "⚠️ هذه الأداة تساعد في التشخيص. المراجعة النهائية تتطلب أخصائي أمراض دم معتمد.",
        "footer": "© 2024 رؤية الشميري الذكية | حلول التصوير الطبي المتقدمة",
        "dataset_title": "📊 قواعد البيانات والتقييم",
        "train_set": "مجموعة التدريب",
        "train_count": "17,000+",
        "test_a": "اختبار-A",
        "test_a_count": "5,000",
        "test_b": "اختبار-B",
        "test_b_count": "4,500",
        "total_eval": "إجمالي التقييم",
        "total_eval_count": "9,500",
        "about_title": "ℹ️ حول",
        "about_developer": "👨‍💻 المطور",
        "about_dev_name": "المهندس يونس عبدالغني الشميري",
        "about_project": "📋 ملخص المشروع",
        "about_project_text": "WBC Vision AI هو نظام دعم قرار سريري (CDSS) قائم على التعلم العميق لتصنيف خلايا الدم البيضاء (WBC) تلقائياً من صور مسحات الدم المحيطية. يستخدم النظام بنية EfficientNet-V2-S ويحقق دقة 99.28% عبر 5 فئات: العدلات، اللمفاويات، الوحيدات، الحمضات، والقاعديات.",
        "about_system": "🔬 نظرة عامة على النظام",
        "about_system_text": "يوفر النظام تشخيصاً مساعداً بالذكاء الاصطناعي في الوقت الفعلي مع تصور Grad-CAM، وقدرة على المعالجة المجمعة، ولوحة تحليلات شاملة. يعمل كأداة بمستوى مستشفى لمساعدة أخصائيي أمراض الدم في الفحص الأولي وتصنيف اضطرابات خلايا الدم.",
        "about_future": "🚀 التطوير المستقبلي",
        "about_future_text": "التعزيزات المخططة تشمل: كشف كريات الدم الحمراء والصفائح، أتمتة CBC الكامل، النشر السحابي للوصول متعدد المستشفيات، التكامل مع أنظمة LIS/HIS، ومسار الحصول على شهادة جهاز طبي FDA/CE.",
        "contact_email": "📧 alshameeri.ai.eng@gmail.com",
        "contact_whatsapp": "📱 +967 773 792 775",
        "menu_about": "عن المشروع",
        "menu_developer": "معلومات المطور",
        "menu_system": "معلومات النظام",
        "project_summary_title": "🧬 نظرة عامة على المشروع",
        "project_summary_text": "نظام تصنيف متقدم للصور الطبية قائم على التعلم العميق للتعرف التلقائي على خمسة أنواع من خلايا الدم البيضاء باستخدام تقنيات رؤية الحاسوب المتطورة. تم تدريب النموذج على أكثر من 17,000 صورة طبية مصنفة وتقييمه على مجموعتين خارجيتين غير مرئيتين (اختبار-A: 5,000 صورة، اختبار-B: 4,500 صورة)، محققاً دقة ممتازة وأداء تعميم قوي.",
        "model_arch": "🏗️ البنية",
        "model_arch_text": "EfficientNet-V2-S (نقل التعلم) بإطار عمل PyTorch",
        "techniques": "🔧 التقنيات",
        "techniques_list": [
            "CrossEntropyLoss مع تنعيم التسميات",
            "محسن AdamW مع جدولة Cosine Annealing",
            "التدريب بدقة مختلطة (AMP/GradScaler)",
            "تعزيز البيانات: دوران، انعكاس، تغيير الألوان",
            "AI قابل للتفسير: مصفوفة الارتباك، منحنى ROC، AUC"
        ],
        "performance": "📈 الأداء",
        "performance_list": [
            "دقة التدريب: >99.5%",
            "دقة الاختبار الخارجي: ~98.99%",
            "تعميم قوي على مجموعات غير مرئية",
            "تقرير تصنيف مفصل وتحليل ROC-AUC"
        ],
        "future_work": "🔮 العمل المستقبلي",
        "future_work_list": [
            "واجهة مستخدم سريرية جاهزة لمهنيي الرعاية الصحية",
            "التكامل في نظام دعم القرار السريري بجانب السرير",
            "تعزيز موثوقية النموذج وقابلية تفسيره",
            "النشر في بيئات المستشفيات والمختبرات"
        ],
    }
}

t = TEXTS[st.session_state.lang]

# ==================== CHECK GPU ====================
try:
    import torch
    st.session_state.gpu = torch.cuda.is_available()
except:
    st.session_state.gpu = False

# ==================== NAVIGATION BAR ====================
col1, col2, col3 = st.columns([3, 1, 1])

with col1:
    st.markdown(f"""
    <div class="nav-logo">
        <span>🔬</span>
        <span>Al-Shameeri AI Vision</span>
    </div>
    """, unsafe_allow_html=True)

with col2:
    if st.button("🇸🇦 العربية / English 🇺🇸", key="lang_toggle", use_container_width=True):
        toggle_lang()
        st.rerun()

with col3:
    # ═══ قائمة من ثلاث نقاط (معلومات المشروع) ═══
    with st.popover("⋮", use_container_width=True):
        st.markdown(f"### {t['about_title']}")
        
        with st.expander(t["menu_developer"], expanded=False):
            st.markdown(f"""
            <div class="info-dropdown">
                <h4>{t['about_developer']}</h4>
                <p><strong>{t['about_dev_name']}</strong></p>
                <p>📧 alshameeri.ai.eng@gmail.com</p>
                <p>📱 +967 773 792 775 (WhatsApp)</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(t["menu_about"], expanded=False):
            st.markdown(f"""
            <div class="info-dropdown">
                <h4>{t['about_project']}</h4>
                <p>{t['about_project_text']}</p>
            </div>
            """, unsafe_allow_html=True)
        
        with st.expander(t["menu_system"], expanded=False):
            st.markdown(f"""
            <div class="info-dropdown">
                <h4>{t['about_system']}</h4>
                <p>{t['about_system_text']}</p>
                <h4>{t['about_future']}</h4>
                <p>{t['about_future_text']}</p>
            </div>
            """, unsafe_allow_html=True)

# ==================== MEDICAL DISCLAIMER ====================
st.markdown(f"""
<div class="medical-banner">
    <span>⚠️</span>
    <span>{t["medical_warning"]}</span>
</div>
""", unsafe_allow_html=True)

# ==================== HERO IMAGE (صورة الميكروسكوب المحلية) ====================
hero_col1, hero_col2, hero_col3 = st.columns([1, 2, 1])
with hero_col2:
    # ═══ استخدام الصورة المحلية من مجلد assets ═══
    try:
        image_path = Path(__file__).parent / "assets" / "image.png"
        if image_path.exists():
            st.image(str(image_path), use_container_width=True, caption="")
        else:
            # fallback: إذا لم تكن الصورة موجودة، استخدم رابط احتياطي
            st.markdown("""
            <div class="hero-image-container">
                <img src="https://img.magnific.com/71e33506dc77eea9c2c7c8fd384557b1d120f60f.jpg" 
                     class="hero-image" 
                     alt="Medical Microscope AI">
            </div>
            """, unsafe_allow_html=True)
    except Exception as e:
        st.markdown("""
        <div class="hero-image-container">
            <span style="font-size:4rem;">🔬</span>
        </div>
        """, unsafe_allow_html=True)

# ==================== HERO SECTION ====================
st.markdown(f'<p class="hero-brand">{t["brand"]}</p>', unsafe_allow_html=True)
st.markdown(f'<h1 class="hero-title">{t["title"]}</h1>', unsafe_allow_html=True)
st.markdown(f'<p class="hero-subtitle">{t["subtitle"]}</p>', unsafe_allow_html=True)

# ==================== SYSTEM STATUS ====================
st.markdown(f"""
<div class="status-bar">
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{t["model_ready"]}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{t["gpu_status"]}</span>
    </div>
    <div class="status-item">
        <div class="status-dot"></div>
        <span>{t["inference_ready"]}</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== PROJECT SUMMARY (ملخص المشروع المفصل) ====================
with st.expander(t["project_summary_title"], expanded=False):
    st.markdown(f"""
    <div class="project-summary">
        <h3>{t["project_summary_title"]}</h3>
        <p>{t["project_summary_text"]}</p>
        <div style="margin-top:20px;">
            <h4 style="color:#4a90d9;">{t["model_arch"]}</h4>
            <p>{t["model_arch_text"]}</p>
        </div>
        <div style="margin-top:20px;">
            <h4 style="color:#4a90d9;">{t["techniques"]}</h4>
            <ul>
    """, unsafe_allow_html=True)
    for item in t["techniques_list"]:
        st.markdown(f"<li>{item}</li>", unsafe_allow_html=True)
    st.markdown(f"""
            </ul>
        </div>
        <div style="margin-top:20px;">
            <h4 style="color:#4a90d9;">{t["performance"]}</h4>
            <ul>
    """, unsafe_allow_html=True)
    for item in t["performance_list"]:
        st.markdown(f"<li>{item}</li>", unsafe_allow_html=True)
    st.markdown(f"""
            </ul>
        </div>
        <div style="margin-top:20px;">
            <h4 style="color:#4a90d9;">{t["future_work"]}</h4>
            <ul>
    """, unsafe_allow_html=True)
    for item in t["future_work_list"]:
        st.markdown(f"<li>{item}</li>", unsafe_allow_html=True)
    st.markdown("""
            </ul>
        </div>
    </div>
    """, unsafe_allow_html=True)

# ==================== MAIN CARDS (شكل فقط + أزرار منفصلة) ====================
col1, col2, col3 = st.columns(3)

with col1:
    st.markdown(f"""
    <div class="glass-card">
        <span class="icon">🔬</span>
        <h3>{t["diagnosis_title"]}</h3>
        <p>{t["diagnosis_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
  if st.button(t["start_btn"], key="btn_diagnosis", use_container_width=True):
    with st.spinner("🔄 Loading AI Engine..."):
        time.sleep(0.5)
    st.switch_page("1_diagnosis")

with col2:
    st.markdown(f"""
    <div class="glass-card">
        <span class="icon">📁</span>
        <h3>{t["batch_title"]}</h3>
        <p>{t["batch_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(t["batch_btn"], key="btn_batch", use_container_width=True):
        with st.spinner("🔄 Loading Batch Processor..."):
            time.sleep(0.5)
        st.switch_page("2_batch")

with col3:
    st.markdown(f"""
    <div class="glass-card">
        <span class="icon">📊</span>
        <h3>{t["dashboard_title"]}</h3>
        <p>{t["dashboard_desc"]}</p>
    </div>
    """, unsafe_allow_html=True)
    
    if st.button(t["dashboard_btn"], key="btn_dashboard", use_container_width=True):
        with st.spinner("🔄 Loading Dashboard..."):
            time.sleep(0.5)
        st.switch_page("3_dashboard")

# ==================== DATASET STATS (قواعد البيانات) ====================
st.markdown(f"""
<div class="dataset-section">
    <div class="dataset-title">{t["dataset_title"]}</div>
    <div class="dataset-grid">
        <div class="dataset-box">
            <span class="number">{t["train_count"]}</span>
            <div class="label">{t["train_set"]}</div>
        </div>
        <div class="dataset-box">
            <span class="number">{t["test_a_count"]}</span>
            <div class="label">{t["test_a"]}</div>
        </div>
        <div class="dataset-box">
            <span class="number">{t["test_b_count"]}</span>
            <div class="label">{t["test_b"]}</div>
        </div>
        <div class="dataset-box">
            <span class="number">{t["total_eval_count"]}</span>
            <div class="label">{t["total_eval"]}</div>
        </div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== STATS ====================
st.markdown(f"""
<div class="stats-grid">
    <div class="stat-box">
        <span class="number">{t["accuracy"]}</span>
        <div class="label">{t["accuracy_label"]}</div>
    </div>
    <div class="stat-box">
        <span class="number">{t["classes"]}</span>
        <div class="label">{t["classes_label"]}</div>
    </div>
    <div class="stat-box">
        <span class="number">&lt;50ms</span>
        <div class="label">{t["speed_label"]}</div>
    </div>
    <div class="stat-box">
        <span class="number">{t["samples"]}</span>
        <div class="label">{t["samples_label"]}</div>
    </div>
</div>
""", unsafe_allow_html=True)

# ==================== CONTACT INFO ====================
st.markdown(f"""
<div class="contact-bar">
    <a href="mailto:alshameeri.ai.eng@gmail.com" class="contact-item">
        <span>📧</span>
        <span>alshameeri.ai.eng@gmail.com</span>
    </a>
    <a href="https://wa.me/967773792775" target="_blank" class="contact-item">
        <span>📱</span>
        <span>+967 773 792 775</span>
    </a>
</div>
""", unsafe_allow_html=True)

# ==================== FOOTER ====================
st.markdown(f'<div class="footer-text">{t["footer"]}</div>', unsafe_allow_html=True)



