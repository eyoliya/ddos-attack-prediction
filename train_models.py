"""
train_models.py
---------------
Trains and evaluates three ML models on network traffic data:
  1. Gaussian Naive Bayes  (baseline)
  2. AdaBoost Classifier   (main model)
  3. Random Forest          (comparison)

Produces all visualizations saved to visualizations/
Run: python train_models.py
"""

import numpy as np
import pandas as pd
import matplotlib
matplotlib.use("Agg")  # headless - saves to file instead of popup
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import seaborn as sns
import warnings
import json
import os

from sklearn.model_selection import train_test_split, cross_val_score
from sklearn.naive_bayes import GaussianNB
from sklearn.ensemble import AdaBoostClassifier, RandomForestClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import (
    accuracy_score, classification_report, confusion_matrix,
    roc_curve, auc, precision_recall_curve
)
from sklearn.preprocessing import StandardScaler
import pickle

warnings.filterwarnings("ignore")
os.makedirs("visualizations", exist_ok=True)
os.makedirs("models", exist_ok=True)

# ─── STYLE ────────────────────────────────────────────────────────────────────
NAVY  = "#0D1B2A"
TEAL  = "#0D9488"
LTEAL = "#5EEAD4"
RED   = "#EF4444"
GRAY  = "#64748B"
plt.rcParams.update({
    "figure.facecolor": "white",
    "axes.facecolor":   "#F8FAFC",
    "axes.edgecolor":   "#E2E8F0",
    "axes.labelcolor":  NAVY,
    "xtick.color":      GRAY,
    "ytick.color":      GRAY,
    "text.color":       NAVY,
    "font.family":      "DejaVu Sans",
    "axes.grid":        True,
    "grid.color":       "#E2E8F0",
    "grid.linewidth":   0.8,
})

# ─── 1. LOAD & EXPLORE DATA ───────────────────────────────────────────────────
print("=" * 60)
print("  DDoS Attack Prediction System — Model Training")
print("=" * 60)

df = pd.read_csv("data/network_traffic.csv")
FEATURE_COLS = [c for c in df.columns if c != "label"]
X = df[FEATURE_COLS]
y = df["label"]

print(f"\n[1] Dataset loaded: {len(df):,} samples, {len(FEATURE_COLS)} features")
print(f"    Normal traffic : {(y==0).sum():,} ({(y==0).mean()*100:.1f}%)")
print(f"    DDoS attacks   : {(y==1).sum():,} ({(y==1).mean()*100:.1f}%)")

# ─── 2. CORRELATION HEATMAP + FEATURE SELECTION ───────────────────────────────
print("\n[2] Computing correlation matrix and selecting features...")

corr = X.corr().abs()

# Plot full correlation heatmap
fig, ax = plt.subplots(figsize=(14, 11))
mask = np.triu(np.ones_like(corr, dtype=bool))
sns.heatmap(
    corr, mask=mask, cmap="YlOrRd", vmin=0, vmax=1,
    annot=False, linewidths=0.4, ax=ax,
    cbar_kws={"shrink": 0.8, "label": "Absolute Correlation"}
)
ax.set_title("Feature Correlation Heatmap\n(Identifying Redundant Features for Removal)",
             fontsize=14, fontweight="bold", color=NAVY, pad=15)
ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha="right", fontsize=8)
ax.set_yticklabels(ax.get_yticklabels(), rotation=0, fontsize=8)
plt.tight_layout()
plt.savefig("visualizations/01_correlation_heatmap.png", dpi=150, bbox_inches="tight")
plt.close()
print("    → Saved: visualizations/01_correlation_heatmap.png")

# Drop highly correlated features (threshold > 0.90)
upper = corr.where(np.triu(np.ones(corr.shape), k=1).astype(bool))
to_drop = [col for col in upper.columns if any(upper[col] > 0.90)]
print(f"    Features dropped (corr > 0.90): {to_drop}")

X_reduced = X.drop(columns=to_drop)
KEPT_FEATURES = list(X_reduced.columns)
print(f"    Features remaining: {len(KEPT_FEATURES)} (was {len(FEATURE_COLS)})")

# ─── 3. TRAIN / TEST SPLIT ────────────────────────────────────────────────────
X_train, X_test, y_train, y_test = train_test_split(
    X_reduced, y, test_size=0.20, random_state=42, stratify=y
)
scaler = StandardScaler()
X_train_sc = scaler.fit_transform(X_train)
X_test_sc  = scaler.transform(X_test)

print(f"\n[3] Train/Test split: {len(X_train):,} train | {len(X_test):,} test")

# ─── 4. TRAIN MODELS ──────────────────────────────────────────────────────────
print("\n[4] Training models...")

gnb = GaussianNB()
gnb.fit(X_train_sc, y_train)

ada = AdaBoostClassifier(
    estimator=DecisionTreeClassifier(max_depth=1),
    n_estimators=100, learning_rate=0.8, random_state=42
)
ada.fit(X_train_sc, y_train)

rf = RandomForestClassifier(n_estimators=100, max_depth=10, random_state=42, n_jobs=-1)
rf.fit(X_train_sc, y_train)

models = {
    "Gaussian Naive Bayes": gnb,
    "AdaBoost":             ada,
    "Random Forest":        rf,
}

# ─── 5. EVALUATE ──────────────────────────────────────────────────────────────
print("\n[5] Evaluation Results:")
print("-" * 50)

results = {}
for name, model in models.items():
    y_pred = model.predict(X_test_sc)
    y_prob = model.predict_proba(X_test_sc)[:, 1]
    acc    = accuracy_score(y_test, y_pred)
    fpr, tpr, _ = roc_curve(y_test, y_prob)
    roc_auc = auc(fpr, tpr)
    cv_scores = cross_val_score(model, X_train_sc, y_train, cv=5, scoring="accuracy")

    results[name] = {
        "accuracy":  acc,
        "auc":       roc_auc,
        "cv_mean":   cv_scores.mean(),
        "cv_std":    cv_scores.std(),
        "y_pred":    y_pred,
        "y_prob":    y_prob,
        "fpr":       fpr,
        "tpr":       tpr,
        "report":    classification_report(y_test, y_pred, target_names=["Normal","DDoS"])
    }
    print(f"\n  {name}")
    print(f"    Accuracy : {acc*100:.2f}%")
    print(f"    ROC-AUC  : {roc_auc:.4f}")
    print(f"    CV Score : {cv_scores.mean()*100:.2f}% ± {cv_scores.std()*100:.2f}%")
    print(results[name]["report"])

# ─── 6. VISUALIZATION: ACCURACY BAR CHART ─────────────────────────────────────
fig, ax = plt.subplots(figsize=(9, 5))
names = list(results.keys())
accs  = [results[n]["accuracy"] * 100 for n in names]
colors = [GRAY, TEAL, NAVY]

bars = ax.bar(names, accs, color=colors, width=0.5, edgecolor="white", linewidth=1.5)
for bar, val in zip(bars, accs):
    ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.3,
            f"{val:.2f}%", ha="center", va="bottom", fontweight="bold", fontsize=12, color=NAVY)

ax.set_ylim(60, 102)
ax.set_ylabel("Accuracy (%)", fontsize=12)
ax.set_title("Model Accuracy Comparison", fontsize=14, fontweight="bold", color=NAVY, pad=15)
ax.axhline(y=90, color=RED, linestyle="--", linewidth=1, alpha=0.6, label="90% threshold")
ax.legend(fontsize=10)
plt.tight_layout()
plt.savefig("visualizations/02_accuracy_comparison.png", dpi=150, bbox_inches="tight")
plt.close()
print("\n    → Saved: visualizations/02_accuracy_comparison.png")

# ─── 7. VISUALIZATION: ROC CURVES ─────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(8, 6))
line_colors = [GRAY, TEAL, NAVY]
for (name, res), col in zip(results.items(), line_colors):
    ax.plot(res["fpr"], res["tpr"], color=col, linewidth=2.5,
            label=f'{name} (AUC = {res["auc"]:.3f})')
ax.plot([0,1],[0,1], "k--", linewidth=1, alpha=0.5, label="Random Classifier")
ax.fill_between(results["AdaBoost"]["fpr"], results["AdaBoost"]["tpr"],
                alpha=0.08, color=TEAL)
ax.set_xlabel("False Positive Rate", fontsize=12)
ax.set_ylabel("True Positive Rate", fontsize=12)
ax.set_title("ROC Curves — All Models", fontsize=14, fontweight="bold", color=NAVY, pad=15)
ax.legend(loc="lower right", fontsize=10)
plt.tight_layout()
plt.savefig("visualizations/03_roc_curves.png", dpi=150, bbox_inches="tight")
plt.close()
print("    → Saved: visualizations/03_roc_curves.png")

# ─── 8. VISUALIZATION: CONFUSION MATRICES ─────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(15, 4))
for ax, (name, res) in zip(axes, results.items()):
    cm = confusion_matrix(y_test, res["y_pred"])
    sns.heatmap(cm, annot=True, fmt="d", cmap="YlOrRd",
                xticklabels=["Normal","DDoS"], yticklabels=["Normal","DDoS"],
                ax=ax, linewidths=1, cbar=False,
                annot_kws={"size": 14, "weight": "bold"})
    ax.set_title(name, fontsize=12, fontweight="bold", color=NAVY)
    ax.set_xlabel("Predicted", fontsize=10)
    ax.set_ylabel("Actual", fontsize=10)
fig.suptitle("Confusion Matrices", fontsize=14, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout()
plt.savefig("visualizations/04_confusion_matrices.png", dpi=150, bbox_inches="tight")
plt.close()
print("    → Saved: visualizations/04_confusion_matrices.png")

# ─── 9. VISUALIZATION: FEATURE IMPORTANCE (AdaBoost) ─────────────────────────
importances = ada.feature_importances_
feat_df = pd.DataFrame({"feature": KEPT_FEATURES, "importance": importances})
feat_df = feat_df.sort_values("importance", ascending=True).tail(12)

fig, ax = plt.subplots(figsize=(9, 6))
bars = ax.barh(feat_df["feature"], feat_df["importance"],
               color=[TEAL if v > feat_df["importance"].median() else LTEAL
                      for v in feat_df["importance"]],
               edgecolor="white", linewidth=0.8)
for bar, val in zip(bars, feat_df["importance"]):
    ax.text(val + 0.001, bar.get_y() + bar.get_height()/2,
            f"{val:.3f}", va="center", fontsize=9, color=NAVY)
ax.set_xlabel("Feature Importance Score", fontsize=12)
ax.set_title("Top Features — AdaBoost Model\n(What the model relies on most to detect attacks)",
             fontsize=13, fontweight="bold", color=NAVY, pad=12)
plt.tight_layout()
plt.savefig("visualizations/05_feature_importance.png", dpi=150, bbox_inches="tight")
plt.close()
print("    → Saved: visualizations/05_feature_importance.png")

# ─── 10. VISUALIZATION: PACKET RATE DISTRIBUTION ─────────────────────────────
fig, axes = plt.subplots(1, 2, figsize=(12, 5))
for ax, col, title in zip(
    axes,
    ["flow_packets_per_sec", "syn_flag_count"],
    ["Packets Per Second Distribution", "SYN Flag Count Distribution"]
):
    normal_vals = df[df.label == 0][col].clip(upper=df[col].quantile(0.99))
    ddos_vals   = df[df.label == 1][col].clip(upper=df[col].quantile(0.99))
    ax.hist(normal_vals, bins=50, alpha=0.7, color=TEAL, label="Normal", density=True)
    ax.hist(ddos_vals,   bins=50, alpha=0.7, color=RED,  label="DDoS Attack", density=True)
    ax.set_title(title, fontsize=12, fontweight="bold", color=NAVY)
    ax.set_xlabel(col.replace("_", " ").title(), fontsize=10)
    ax.set_ylabel("Density", fontsize=10)
    ax.legend(fontsize=10)
fig.suptitle("Key Feature Distributions: Normal vs DDoS Traffic",
             fontsize=14, fontweight="bold", color=NAVY, y=1.02)
plt.tight_layout()
plt.savefig("visualizations/06_feature_distributions.png", dpi=150, bbox_inches="tight")
plt.close()
print("    → Saved: visualizations/06_feature_distributions.png")

# ─── 11. SAVE MODELS & RESULTS ────────────────────────────────────────────────
print("\n[6] Saving models and results...")
pickle.dump(gnb, open("models/naive_bayes.pkl", "wb"))
pickle.dump(ada, open("models/adaboost.pkl", "wb"))
pickle.dump(rf,  open("models/random_forest.pkl", "wb"))
pickle.dump(scaler, open("models/scaler.pkl", "wb"))
with open("models/feature_cols.json", "w") as f:
    json.dump(KEPT_FEATURES, f)

# Save summary
summary = {
    model: {
        "accuracy_pct": round(res["accuracy"]*100, 2),
        "roc_auc":       round(res["auc"], 4),
        "cv_mean_pct":   round(res["cv_mean"]*100, 2),
        "cv_std_pct":    round(res["cv_std"]*100, 2),
    }
    for model, res in results.items()
}
with open("models/results_summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n" + "=" * 60)
print("  COMPLETE. All models trained, visualizations saved.")
print("  Best model: AdaBoost")
best = results["AdaBoost"]
print(f"  Accuracy : {best['accuracy']*100:.2f}%")
print(f"  ROC-AUC  : {best['auc']:.4f}")
print("=" * 60)
