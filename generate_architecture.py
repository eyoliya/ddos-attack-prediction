"""
generate_architecture.py
-------------------------
Generates a clean system architecture diagram for the presentation.
Shows the full data flow from traffic → model → API → Docker → AWS.
Run: python generate_architecture.py
"""

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import os

os.makedirs("visualizations", exist_ok=True)

# ─── Colors ───────────────────────────────────────────────────────────────────
NAVY   = "#0D1B2A"
TEAL   = "#0D9488"
LTEAL  = "#CCFBF1"
WHITE  = "#FFFFFF"
GRAY   = "#64748B"
LGRAY  = "#F1F5F9"
ORANGE = "#F59E0B"
RED    = "#EF4444"
GREEN  = "#10B981"
PURPLE = "#7C3AED"

fig, ax = plt.subplots(figsize=(16, 9))
ax.set_xlim(0, 16)
ax.set_ylim(0, 9)
ax.axis("off")
fig.patch.set_facecolor(NAVY)
ax.set_facecolor(NAVY)

def box(x, y, w, h, color, radius=0.3, edge=WHITE, lw=1.5):
    rect = FancyBboxPatch((x, y), w, h,
        boxstyle=f"round,pad=0,rounding_size={radius}",
        facecolor=color, edgecolor=edge, linewidth=lw, zorder=3)
    ax.add_patch(rect)

def arrow(x1, y1, x2, y2, color=TEAL, lw=2):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
        arrowprops=dict(arrowstyle="-|>", color=color,
                        lw=lw, mutation_scale=15),
        zorder=4)

def label(x, y, text, size=9, color=WHITE, bold=False, ha="center", va="center"):
    ax.text(x, y, text, fontsize=size, color=color,
            ha=ha, va=va, fontweight="bold" if bold else "normal",
            zorder=5)

# ─── Title ────────────────────────────────────────────────────────────────────
label(8, 8.5, "DDoS Attack Prediction System — Architecture", size=16, bold=True)
label(8, 8.1, "End-to-end ML pipeline: from raw network traffic to cloud-native deployment", size=10, color=TEAL)

# ─── Layer labels (left side) ─────────────────────────────────────────────────
for y, txt in [(6.8, "DATA LAYER"), (5.1, "ML LAYER"), (3.3, "API LAYER"), (1.4, "CLOUD LAYER")]:
    ax.text(0.15, y, txt, fontsize=7, color=GRAY, fontweight="bold",
            rotation=90, va="center", ha="center", zorder=5)

# ═══════════════════════════════════════════════════════════════════
# ROW 1 — DATA LAYER
# ═══════════════════════════════════════════════════════════════════
# Network traffic input
box(0.5, 6.3, 2.5, 1.0, GRAY, edge=GRAY)
label(1.75, 6.95, "Network Traffic", size=9, bold=True)
label(1.75, 6.6,  "15,000 flow samples", size=8, color=LTEAL)
label(1.75, 6.4,  "23 raw features", size=8, color=LTEAL)

arrow(3.05, 6.8, 3.5, 6.8)

# Feature engineering
box(3.5, 6.3, 3.0, 1.0, "#1E3A5F", edge=TEAL, lw=2)
label(5.0, 6.95, "Feature Engineering", size=9, bold=True, color=TEAL)
label(5.0, 6.65, "Correlation heatmap", size=8)
label(5.0, 6.45, "Drop 3 redundant features → 20 kept", size=7.5)

arrow(6.55, 6.8, 7.0, 6.8)

# Dataset stats
box(7.0, 6.3, 2.8, 1.0, GRAY)
label(8.4, 6.95, "Clean Dataset", size=9, bold=True)
label(8.4, 6.65, "53% Normal  |  47% DDoS", size=8, color=LTEAL)
label(8.4, 6.45, "Train 80% / Test 20%", size=8, color=LTEAL)

# ═══════════════════════════════════════════════════════════════════
# ROW 2 — ML LAYER
# ═══════════════════════════════════════════════════════════════════
arrow(8.4, 6.3, 8.4, 5.8)

# 3 model boxes
model_data = [
    (1.0, "Gaussian\nNaive Bayes", "98.4% acc", GRAY),
    (5.0, "AdaBoost (Primary)", "~100% acc\n(primary)", "#0F4C3A"),
    (9.2, "Random\nForest", "~100% acc", GRAY),
]
for mx, name, acc, col in model_data:
    box(mx, 4.7, 2.6, 1.0, col, edge=TEAL if "Ada" in name else GRAY,
        lw=2.5 if "Ada" in name else 1.5)
    label(mx+1.3, 5.35, name, size=9, bold=True,
          color=TEAL if "Ada" in name else WHITE)
    label(mx+1.3, 4.95, acc, size=8,
          color=LTEAL if "Ada" in name else LGRAY)

# Arrow to AdaBoost
arrow(8.4, 5.8, 6.3, 5.7)

# Results badge
box(10.2, 4.7, 2.8, 1.0, "#1E3A5F", edge=GREEN, lw=2)
label(11.6, 5.35, "Results", size=9, bold=True, color=GREEN)
label(11.6, 5.08, "ROC-AUC: 0.9998", size=8, color=LTEAL)
label(11.6, 4.88, "CV: 99.99% ± 0.02%", size=8, color=LTEAL)

# ═══════════════════════════════════════════════════════════════════
# ROW 3 — API LAYER
# ═══════════════════════════════════════════════════════════════════
arrow(6.3, 4.7, 6.3, 4.15)

# Flask API box
box(4.2, 3.1, 4.2, 1.0, "#1E3A5F", edge=ORANGE, lw=2)
label(6.3, 3.72, "Flask REST API  (app.py)", size=10, bold=True, color=ORANGE)
label(6.3, 3.42, "GET /health   GET /model-info", size=8)
label(6.3, 3.22, "POST /predict → JSON response   GET /demo", size=8)

arrow(4.2, 3.6, 3.5, 3.6)
arrow(8.4, 3.6, 9.1, 3.6)

# Docker box (left of Flask)
box(1.0, 3.1, 2.4, 1.0, "#1a1a2e", edge=ORANGE)
label(2.2, 3.72, "Docker", size=9, bold=True, color=ORANGE)
label(2.2, 3.48, "Containerized", size=8)
label(2.2, 3.28, "Runs anywhere", size=8)

# Clients (right of Flask)
box(9.1, 3.1, 2.5, 1.0, GRAY)
label(10.35, 3.72, "Clients", size=9, bold=True)
label(10.35, 3.48, "curl / Postman", size=8, color=LTEAL)
label(10.35, 3.28, "Any HTTP client", size=8, color=LTEAL)

# ═══════════════════════════════════════════════════════════════════
# ROW 4 — CLOUD LAYER
# ═══════════════════════════════════════════════════════════════════
arrow(6.3, 3.1, 6.3, 2.55)

# AWS wrapper box
box(0.6, 0.7, 14.8, 1.8, "#0a2540", edge=ORANGE, lw=1.5, radius=0.4)
label(8.0, 2.35, "AWS Free Tier", size=9, bold=True, color=ORANGE)

# S3 box
box(1.2, 0.9, 3.5, 1.1, "#1E3A5F", edge=TEAL)
label(2.95, 1.6, "S3 Bucket", size=9, bold=True, color=TEAL)
label(2.95, 1.35, "Model artifacts stored", size=8)
label(2.95, 1.1,  "adaboost.pkl  scaler.pkl", size=7.5, color=LTEAL)

# CloudWatch box
box(5.2, 0.9, 4.0, 1.1, "#1E3A5F", edge=GREEN)
label(7.2, 1.6,  "CloudWatch", size=9, bold=True, color=GREEN)
label(7.2, 1.35, "Custom metrics dashboard", size=8)
label(7.2, 1.1,  "Attack rate · Confidence · Latency", size=7.5, color=LTEAL)

# IAM box
box(9.8, 0.9, 2.5, 1.1, "#1E3A5F", edge=GRAY)
label(11.05, 1.6,  "IAM", size=9, bold=True)
label(11.05, 1.35, "Access control", size=8)
label(11.05, 1.1,  "Secure credentials", size=7.5, color=LTEAL)

# Deployment note
box(12.5, 0.9, 2.6, 1.1, "#1E3A5F", edge=GRAY)
label(13.8, 1.6,  "Deploy Path", size=9, bold=True)
label(13.8, 1.35, "EC2 / ECS", size=8)
label(13.8, 1.1,  "Container hosting", size=7.5, color=LTEAL)

# Arrows to AWS services
arrow(6.3, 2.55, 3.2, 2.0)   # → S3
arrow(6.3, 2.55, 7.2, 2.0)   # → CloudWatch

# ─── Legend ───────────────────────────────────────────────────────────────────
legend_items = [
    (TEAL,   "Core ML Pipeline"),
    (ORANGE, "Deployment / API"),
    (GREEN,  "Monitoring"),
    (GRAY,   "Supporting Components"),
]
for i, (col, txt) in enumerate(legend_items):
    lx = 10.5 + i * 1.35
    box(lx - 0.08, 0.25, 0.18, 0.18, col, radius=0.05, edge=col)
    label(lx + 0.55, 0.34, txt, size=7.5, color=WHITE, ha="left")

plt.tight_layout(pad=0)
plt.savefig("visualizations/00_architecture.png", dpi=150,
            bbox_inches="tight", facecolor=NAVY)
plt.close()
print("Saved: visualizations/00_architecture.png")
