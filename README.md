# 🛡️ DDoS Attack Prediction System

**Predicting Distributed Denial-of-Service attacks before they peak using Machine Learning**

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://python.org)
[![scikit-learn](https://img.shields.io/badge/scikit--learn-1.3+-orange.svg)](https://scikit-learn.org)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

---

## 🎯 The Problem

Traditional network security tools **react after an attack starts** — by the time an alert fires, servers are already overwhelmed and services are down. The average DDoS attack costs **$2.5 million** in downtime and damages.

**This project flips the approach:** using machine learning on network flow features to predict DDoS attacks *before* they fully materialize, enabling pre-emptive defense.

---

## 🧠 How It Works

```
Raw Network Traffic
        ↓
  Feature Extraction (22 flow metrics)
        ↓
  Correlation Analysis → Drop redundant features
        ↓
  ML Classification (AdaBoost)
        ↓
  ⚡ Prediction + Auto-Response
    ├── Normal → Allow traffic
    └── DDoS   → Trigger firewall rules, alert team
```

---

## 📊 Results

| Model                | Accuracy  | ROC-AUC  | CV Score        |
|----------------------|-----------|----------|-----------------|
| Gaussian Naive Bayes | ~82%      | ~0.91    | 82% ± 0.5%      |
| **AdaBoost** ⭐      | **~95%**  | **~0.99**| **95% ± 0.3%**  |
| Random Forest        | ~96%      | ~0.99    | 96% ± 0.2%      |

> AdaBoost chosen as primary model: near-identical accuracy to Random Forest but with **3× faster inference** — critical for real-time traffic analysis.

---

## 🔍 Key Findings

1. **Feature selection mattered more than algorithm choice** — dropping correlated features (>0.90 threshold) via heatmap analysis improved all models
2. **Top predictive features:** `flow_packets_per_sec`, `syn_flag_count`, `fwd_iat_mean` — DDoS traffic shows extreme packet rates and near-zero inter-arrival times
3. **AdaBoost's iterative learning** handles the edge cases that Naive Bayes misses (Naive Bayes assumes feature independence, which doesn't hold for network traffic)

---

## 🚀 Quick Start

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

### 2. Generate dataset
```bash
python generate_dataset.py
```

### 3. Train all models + generate visualizations
```bash
python train_models.py
```

### 4. Run the live demo
```bash
python demo/predict.py
```

---

## 📁 Project Structure

```
ddos_project/
├── generate_dataset.py      # Synthetic network traffic dataset
├── train_models.py          # Model training + all visualizations
├── demo/
│   └── predict.py           # Live real-time prediction demo
├── data/
│   └── network_traffic.csv  # Generated dataset (15,000 samples)
├── models/
│   ├── adaboost.pkl         # Trained AdaBoost model
│   ├── naive_bayes.pkl      # Trained Naive Bayes model
│   ├── random_forest.pkl    # Trained Random Forest model
│   ├── scaler.pkl           # StandardScaler
│   └── feature_cols.json    # Selected feature names
├── visualizations/
│   ├── 01_correlation_heatmap.png
│   ├── 02_accuracy_comparison.png
│   ├── 03_roc_curves.png
│   ├── 04_confusion_matrices.png
│   ├── 05_feature_importance.png
│   └── 06_feature_distributions.png
└── requirements.txt
```

---

## 📈 Visualizations

### Feature Correlation Heatmap
Used to identify and remove redundant features before training.

### ROC Curves
AdaBoost and Random Forest both achieve AUC ≈ 0.99 — near-perfect discrimination between normal and attack traffic.

### Feature Importance
The model relies most on packet rate metrics and SYN flag counts — exactly the signatures that DDoS attacks exhibit.

---

## 🔧 Technical Details

**Dataset:** Synthetic network flow data (15,000 samples) structured after the CIC-DDoS2019 benchmark dataset. Features include inter-arrival times, packet lengths, byte counts, TCP flag counts, and flow duration metrics.

**Models:**
- **Gaussian Naive Bayes** — probabilistic baseline using Bayes' theorem with Gaussian feature distributions
- **AdaBoost** — ensemble of 100 weak decision stumps, each iteration focusing on misclassified samples
- **Random Forest** — 100 decision trees with max_depth=10 for comparison

**Preprocessing:** StandardScaler normalization + correlation-based feature elimination (threshold: 0.90)

---

## ☁️ Cloud Deployment Path

This model can be deployed to protect cloud infrastructure:

```
AWS / GCP / Azure
       ↓
  VPC Flow Logs → Lambda / Cloud Function
       ↓
  Model Inference (<1ms per flow)
       ↓
  Auto-trigger: WAF rules, IP blocking, scale-up
```

---

## 👤 Author

**Amogh Nellutla** — M.S. Cybersecurity, Montclair State University  
[nellutlaamg@gmail.com](mailto:nellutlaamg@gmail.com)

---

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.
