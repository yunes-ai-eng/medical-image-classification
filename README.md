# White Blood Cell (WBC) Classification System

An advanced **Deep Learning–based medical image classification system** for automatic recognition of **five types of White Blood Cells (WBCs)** using state-of-the-art Computer Vision techniques.

---

## 🚀 Project Overview

This project implements a **high-performance CNN model based on EfficientNet-V2-S** to classify white blood cell images into the following categories:

- Basophil  
- Eosinophil  
- Lymphocyte  
- Monocyte  
- Neutrophil  

The model was trained on **17,000+ labeled medical images** and evaluated on **two completely unseen external datasets**, achieving **excellent accuracy and strong generalization performance**.
The datasets used include labeled microscopic blood cell images collected from multiple public medical sources.
---

## 🧠 Model & Techniques

- **Architecture:** EfficientNet-V2-S (Transfer Learning)
- **Framework:** PyTorch
- **Loss Function:** CrossEntropyLoss with Label Smoothing
- **Optimizer:** AdamW
- **Scheduler:** Cosine Annealing Learning Rate
- **Mixed Precision Training:** AMP (GradScaler)
- **Data Augmentation:** Rotation, Flip, Color Jitter
- **Explainable AI:** Confusion Matrix, ROC Curve, AUC

---

## 📊 Performance Highlights

- **Training Accuracy:** >99.5%
- **External Test Accuracy:** ~98.99%
- **Strong generalization on unseen datasets**
- Detailed **classification report and ROC-AUC analysis** for each class

---

## Visual Evaluation

- Learning Curves (Accuracy & Loss)
- Confusion Matrix Visualization
- Multi-Class ROC Curves (AUC)

---

## User Interface

A simple **user-friendly interface** was developed where users can:
- Upload a blood cell image
- Automatically classify the WBC type in real-time

---
## Technologies Used

- Python
- PyTorch & TorchVision
- NumPy, Pandas
- OpenCV
- Matplotlib, Seaborn
- Scikit-learn

## 📦 Trained Model
The trained model file is not included due to size limitations.  
It can be provided upon request or shared via cloud storage.
  
## Development Environment

- Google Colab (GPU-accelerated training)
- Python 3
- CUDA-enabled environment
  
  ## Future Work
- Development of a **clinical-ready user interface or application** that allows medical professionals to upload blood cell images and receive real-time WBC classification results.
- Integration of the trained deep learning model into a **bedside clinical decision support system**.
- Enhancing model reliability and interpretability for **safe clinical usage**.
- Preparing the system for **hospital and laboratory environments**.
  
## Project Structure
medical-image-classification/
├── data/
│   └── Train/
├── training/
│   └── wbc_training.py
├── models/
│   └── best_wbc_ultimate.pth
├── ui/
│   └── app.py
├── README.md

---

##  Author

**Yunes Abdulghani Mohammed Ghaleb**  
AI Engineer | Machine Learning & Computer Vision  
📍 Open to relocate internationally

⚠️ This project is intended for research and educational purposes only and should not be used as a standalone medical diagnostic system.
