"""
aws/log_prediction.py
----------------------
Logs every prediction as a custom metric to AWS CloudWatch.

CloudWatch is AWS's monitoring and observability service.
Every time the model makes a prediction, we send:
  - Was it an attack? (1 or 0)
  - How confident? (0-100%)
  - How fast was inference? (milliseconds)

This creates a LIVE DASHBOARD in AWS showing:
  - Attack frequency over time (graph)
  - Confidence score trends
  - API response times
  - You can set ALARMS: "alert me if >10 attacks/minute"

AWS Free Tier: CloudWatch gives you 10 custom metrics free for 12 months.

Usage (standalone test):
    python aws/log_prediction.py

Used by app.py automatically when AWS credentials are configured.
"""

import os
import sys
import json
from datetime import datetime, timezone

try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
    BOTO3_AVAILABLE = True
except ImportError:
    BOTO3_AVAILABLE = False

# ─── Config ───────────────────────────────────────────────────────────────────
NAMESPACE   = "DDoSPredictionSystem"   # Groups all our metrics in CloudWatch
REGION      = "us-east-1"
ENVIRONMENT = "production"

# ─── CloudWatch Logger ────────────────────────────────────────────────────────
class CloudWatchLogger:
    """
    Sends prediction events to CloudWatch as custom metrics.
    Falls back silently if AWS credentials aren't configured —
    so the app keeps working even without AWS set up.
    """

    def __init__(self, namespace=NAMESPACE, region=REGION):
        self.namespace = namespace
        self.enabled   = False

        if not BOTO3_AVAILABLE:
            return

        try:
            self.cw      = boto3.client("cloudwatch", region_name=region)
            self.enabled = True
        except Exception:
            pass  # Fail silently — app works without AWS

    def log_prediction(self, is_attack: bool, confidence_pct: float,
                       inference_ms: float, source: str = "api"):
        """
        Sends 3 metrics to CloudWatch for a single prediction event.

        Metrics sent:
          - AttackDetected       (0 or 1)
          - PredictionConfidence (0-100)
          - InferenceLatencyMs   (milliseconds)
        """
        if not self.enabled:
            return False

        dimensions = [
            {"Name": "Environment", "Value": ENVIRONMENT},
            {"Name": "Source",      "Value": source},
        ]

        metric_data = [
            {
                "MetricName": "AttackDetected",
                "Dimensions": dimensions,
                "Value":      1.0 if is_attack else 0.0,
                "Unit":       "Count",
                "Timestamp":  datetime.now(timezone.utc),
            },
            {
                "MetricName": "PredictionConfidence",
                "Dimensions": dimensions,
                "Value":      confidence_pct,
                "Unit":       "Percent",
                "Timestamp":  datetime.now(timezone.utc),
            },
            {
                "MetricName": "InferenceLatencyMs",
                "Dimensions": dimensions,
                "Value":      inference_ms,
                "Unit":       "Milliseconds",
                "Timestamp":  datetime.now(timezone.utc),
            },
        ]

        try:
            self.cw.put_metric_data(Namespace=self.namespace, MetricData=metric_data)
            return True
        except Exception:
            return False  # Never crash the app over a logging failure

    def log_batch(self, predictions: list):
        """Log multiple predictions at once (more efficient than one-by-one)."""
        if not self.enabled or not predictions:
            return False

        metric_data = []
        ts = datetime.now(timezone.utc)

        for p in predictions:
            dims = [{"Name": "Environment", "Value": ENVIRONMENT}]
            metric_data.extend([
                {"MetricName": "AttackDetected",
                 "Dimensions": dims, "Value": 1.0 if p["is_attack"] else 0.0,
                 "Unit": "Count", "Timestamp": ts},
                {"MetricName": "PredictionConfidence",
                 "Dimensions": dims, "Value": p.get("confidence_pct", 0),
                 "Unit": "Percent", "Timestamp": ts},
            ])

        try:
            # CloudWatch accepts max 20 metrics per call
            for i in range(0, len(metric_data), 20):
                self.cw.put_metric_data(
                    Namespace=self.namespace,
                    MetricData=metric_data[i:i+20]
                )
            return True
        except Exception:
            return False


def create_dashboard(region=REGION):
    """
    Creates a CloudWatch dashboard showing attack trends.
    Run once after setting up AWS credentials.
    """
    if not BOTO3_AVAILABLE:
        print("boto3 not installed")
        return

    cw = boto3.client("cloudwatch", region_name=region)

    dashboard_body = {
        "widgets": [
            {
                "type": "metric",
                "properties": {
                    "title": "DDoS Attacks Detected Over Time",
                    "metrics": [[NAMESPACE, "AttackDetected",
                                 "Environment", ENVIRONMENT]],
                    "period": 60,
                    "stat":   "Sum",
                    "view":   "timeSeries",
                    "region": region,
                }
            },
            {
                "type": "metric",
                "properties": {
                    "title": "Prediction Confidence %",
                    "metrics": [[NAMESPACE, "PredictionConfidence",
                                 "Environment", ENVIRONMENT]],
                    "period": 60,
                    "stat":   "Average",
                    "view":   "timeSeries",
                    "region": region,
                }
            },
            {
                "type": "metric",
                "properties": {
                    "title": "API Inference Latency (ms)",
                    "metrics": [[NAMESPACE, "InferenceLatencyMs",
                                 "Environment", ENVIRONMENT]],
                    "period": 60,
                    "stat":   "Average",
                    "view":   "timeSeries",
                    "region": region,
                }
            },
        ]
    }

    try:
        cw.put_dashboard(
            DashboardName="DDoS-Prediction-System",
            DashboardBody=json.dumps(dashboard_body)
        )
        print("  Dashboard created!")
        print(f"  https://console.aws.amazon.com/cloudwatch/home?region={region}#dashboards:name=DDoS-Prediction-System")
    except NoCredentialsError:
        print("  AWS credentials not configured. Run 'aws configure'.")
    except Exception as e:
        print(f"  Error creating dashboard: {e}")


# ─── Standalone test ──────────────────────────────────────────────────────────
if __name__ == "__main__":
    print("\n" + "="*55)
    print("  CloudWatch Logger — Test")
    print("="*55)

    logger = CloudWatchLogger()

    if not logger.enabled:
        print("\n  AWS not configured — running in local-only mode.")
        print("  To enable CloudWatch:")
        print("  1. Install AWS CLI: https://aws.amazon.com/cli/")
        print("  2. Run: aws configure")
        print("  3. Enter your Access Key ID and Secret Access Key")
        print("\n  Once configured, this script will send real metrics")
        print("  to your CloudWatch dashboard.\n")
    else:
        print("\n  Sending test metrics to CloudWatch...")

        # Simulate 5 predictions
        test_cases = [
            (False, 26.5, 7.1),   # normal
            (True,  70.0, 6.8),   # attack
            (False, 39.6, 7.3),   # normal
            (True,  85.2, 6.5),   # attack (high confidence)
            (False, 15.0, 7.0),   # normal (very confident)
        ]

        for is_attack, confidence, latency in test_cases:
            ok = logger.log_prediction(is_attack, confidence, latency)
            icon = "🚨" if is_attack else "✅"
            status = "logged ✓" if ok else "failed ✗"
            print(f"  {icon} {'Attack' if is_attack else 'Normal':8} "
                  f"{confidence:5.1f}% confidence — {status}")

        print("\n  View your dashboard:")
        print(f"  https://console.aws.amazon.com/cloudwatch/home?region={REGION}")
        print("  Metrics namespace: DDoSPredictionSystem")
        print("="*55 + "\n")

        # Optionally create dashboard
        create = input("  Create CloudWatch dashboard? (y/n): ").strip().lower()
        if create == "y":
            create_dashboard()
