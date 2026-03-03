"""
app.py
------
Flask REST API for the DDoS Attack Prediction System.

The trained AdaBoost model is exposed as an HTTP endpoint.
Any application, monitoring tool, or cloud service can call it
and get a real-time prediction back as JSON.

Endpoints:
    GET  /health          → confirms the API is running
    GET  /model-info      → shows model details and feature list
    POST /predict         → takes network flow features, returns prediction
    GET  /demo            → runs 3 built-in test cases, returns all results

Run locally:
    python app.py

Then in another terminal:
    curl http://localhost:5000/health
"""

import os
import json
import pickle
import time
import logging
from datetime import datetime, timezone

import numpy as np
import pandas as pd
from flask import Flask, request, jsonify

# AWS CloudWatch logger (fails silently if AWS not configured)
try:
    from aws.log_prediction import CloudWatchLogger
    CW_LOGGER = CloudWatchLogger()
except Exception:
    CW_LOGGER = None

# ─── Setup ────────────────────────────────────────────────────────────────────
app = Flask(__name__)
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger(__name__)

# ─── Load model once at startup ───────────────────────────────────────────────
MODEL_DIR = os.path.join(os.path.dirname(__file__), "models")

def load_artifacts():
    model    = pickle.load(open(os.path.join(MODEL_DIR, "adaboost.pkl"),    "rb"))
    scaler   = pickle.load(open(os.path.join(MODEL_DIR, "scaler.pkl"),      "rb"))
    features = json.load(open(os.path.join(MODEL_DIR, "feature_cols.json")))
    return model, scaler, features

try:
    MODEL, SCALER, FEATURES = load_artifacts()
    log.info(f"Model loaded successfully — {len(FEATURES)} features")
except Exception as e:
    log.error(f"Failed to load model: {e}")
    MODEL, SCALER, FEATURES = None, None, None

# ─── Prediction logic (shared by /predict and /demo) ─────────────────────────
def run_prediction(traffic_dict):
    """
    Takes a dict of network flow features.
    Returns a structured result dict.
    Missing features default to 0.
    """
    vec = pd.DataFrame(
        [[traffic_dict.get(f, 0.0) for f in FEATURES]],
        columns=FEATURES
    )
    vec_scaled = SCALER.transform(vec)

    prob_ddos   = float(MODEL.predict_proba(vec_scaled)[0][1])
    prob_normal = 1.0 - prob_ddos
    is_attack   = prob_ddos >= 0.5

    return {
        "prediction":    "DDoS Attack" if is_attack else "Normal Traffic",
        "is_attack":     is_attack,
        "confidence": {
            "ddos_pct":   round(prob_ddos   * 100, 2),
            "normal_pct": round(prob_normal * 100, 2),
        },
        "action":        "BLOCK — firewall rules triggered" if is_attack else "ALLOW — traffic cleared",
        "timestamp":     datetime.now(timezone.utc).isoformat(),
        "model":         "AdaBoost (100 estimators)",
        "features_used": len(FEATURES),
    }

# ─── Routes ───────────────────────────────────────────────────────────────────

@app.route("/health", methods=["GET"])
def health():
    """Simple health check — confirms API is running and model is loaded."""
    return jsonify({
        "status":       "healthy",
        "model_loaded": MODEL is not None,
        "timestamp":    datetime.now(timezone.utc).isoformat(),
    })


@app.route("/model-info", methods=["GET"])
def model_info():
    """Returns model metadata and the list of expected input features."""
    if MODEL is None:
        return jsonify({"error": "Model not loaded"}), 503

    return jsonify({
        "model_type":    "AdaBoostClassifier",
        "n_estimators":  100,
        "classes":       ["Normal Traffic", "DDoS Attack"],
        "n_features":    len(FEATURES),
        "features":      FEATURES,
        "description":   "Predicts DDoS attacks from network flow statistics",
    })


@app.route("/predict", methods=["POST"])
def predict():
    """
    Main prediction endpoint.

    Expects JSON body with network flow features. Example:
        {
            "flow_packets_per_sec": 6200,
            "fwd_iat_mean": 18,
            "syn_flag_count": 920,
            ...
        }

    Returns prediction, confidence scores, and recommended action.
    """
    if MODEL is None:
        return jsonify({"error": "Model not loaded"}), 503

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    try:
        t_start = time.perf_counter()
        result  = run_prediction(data)
        elapsed = round((time.perf_counter() - t_start) * 1000, 3)
        result["inference_ms"] = elapsed

        log.info(f"Prediction: {result['prediction']} | "
                 f"DDoS confidence: {result['confidence']['ddos_pct']}% | "
                 f"Inference: {elapsed}ms")

        # Log to AWS CloudWatch (silent no-op if AWS not configured)
        if CW_LOGGER:
            CW_LOGGER.log_prediction(
                is_attack=result['is_attack'],
                confidence_pct=result['confidence']['ddos_pct'],
                inference_ms=elapsed,
                source='api'
            )

        return jsonify(result)

    except Exception as e:
        log.error(f"Prediction error: {e}")
        return jsonify({"error": str(e)}), 500


@app.route("/demo", methods=["GET"])
def demo():
    """
    Runs 3 built-in test cases and returns all predictions.
    Great for quickly verifying the API is working correctly.
    """
    if MODEL is None:
        return jsonify({"error": "Model not loaded"}), 503

    samples = [
        {
            "label": "Normal HTTPS Web Traffic",
            "features": {
                "flow_duration": 45000, "total_fwd_packets": 18, "total_bwd_packets": 14,
                "total_len_fwd_packets": 5200, "total_len_bwd_packets": 9800,
                "fwd_packet_len_mean": 290, "bwd_packet_len_mean": 620,
                "flow_bytes_per_sec": 12000, "flow_packets_per_sec": 35,
                "fwd_iat_mean": 2800, "bwd_iat_mean": 3500,
                "fwd_iat_std": 1800, "bwd_iat_std": 2200,
                "psh_flag_count": 4, "ack_flag_count": 12,
                "avg_packet_size": 440, "avg_fwd_segment_size": 280,
                "avg_bwd_segment_size": 590, "active_mean": 9000, "idle_mean": 22000,
            }
        },
        {
            "label": "SYN Flood DDoS Attack",
            "features": {
                "flow_duration": 3000, "total_fwd_packets": 950, "total_bwd_packets": 1,
                "total_len_fwd_packets": 380, "total_len_bwd_packets": 20,
                "fwd_packet_len_mean": 55, "bwd_packet_len_mean": 40,
                "flow_bytes_per_sec": 780000, "flow_packets_per_sec": 6200,
                "fwd_iat_mean": 18, "bwd_iat_mean": 5000,
                "fwd_iat_std": 12, "bwd_iat_std": 4500,
                "psh_flag_count": 2, "ack_flag_count": 1,
                "avg_packet_size": 60, "avg_fwd_segment_size": 55,
                "avg_bwd_segment_size": 38, "active_mean": 200, "idle_mean": 100,
            }
        },
        {
            "label": "Ambiguous Edge Case",
            "features": {
                "flow_duration": 18000, "total_fwd_packets": 120, "total_bwd_packets": 8,
                "total_len_fwd_packets": 1800, "total_len_bwd_packets": 400,
                "fwd_packet_len_mean": 100, "bwd_packet_len_mean": 200,
                "flow_bytes_per_sec": 95000, "flow_packets_per_sec": 320,
                "fwd_iat_mean": 200, "bwd_iat_mean": 3000,
                "fwd_iat_std": 150, "bwd_iat_std": 2800,
                "psh_flag_count": 10, "ack_flag_count": 15,
                "avg_packet_size": 180, "avg_fwd_segment_size": 95,
                "avg_bwd_segment_size": 180, "active_mean": 1500, "idle_mean": 800,
            }
        },
    ]

    results = []
    for s in samples:
        result = run_prediction(s["features"])
        results.append({"label": s["label"], **result})

    return jsonify({
        "demo_results": results,
        "summary": f"Ran {len(results)} test cases successfully",
    })


# ─── Run ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  DDoS Prediction API — Starting")
    print("  http://localhost:5000/health")
    print("  http://localhost:5000/model-info")
    print("  http://localhost:5000/demo")
    print("  POST http://localhost:5000/predict")
    print("="*55 + "\n")
    app.run(host="0.0.0.0", port=5000, debug=False)
