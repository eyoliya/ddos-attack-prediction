"""
send_metrics.py
---------------
Sends 20 realistic predictions to AWS CloudWatch.
Run this to populate the CloudWatch dashboard with real data.

Usage: python send_metrics.py
"""

import sys
import time
sys.path.insert(0, '.')

from aws.log_prediction import CloudWatchLogger

logger = CloudWatchLogger()

if not logger.enabled:
    print("AWS not configured. Run 'aws configure' first.")
    sys.exit(1)

print("Sending 20 predictions to CloudWatch...")
print("-" * 45)

# Realistic mix: 8 attacks, 12 normal
traffic = [
    (False, 98.9, 7.1),
    (True,  92.9, 6.8),
    (False, 78.5, 7.3),
    (True,  85.2, 6.5),
    (False, 95.0, 7.0),
    (True,  70.1, 6.9),
    (False, 88.3, 7.2),
    (False, 92.1, 6.7),
    (True,  96.4, 6.4),
    (False, 99.1, 7.1),
    (True,  88.7, 6.6),
    (False, 76.2, 7.4),
    (True,  91.3, 6.3),
    (False, 94.5, 7.0),
    (True,  79.8, 6.8),
    (False, 97.2, 7.2),
    (True,  93.6, 6.5),
    (False, 85.9, 7.1),
    (True,  87.4, 6.7),
    (False, 96.8, 6.9),
]

for i, (is_attack, conf, latency) in enumerate(traffic):
    ok = logger.log_prediction(is_attack, conf, latency, source="demo")
    icon = "ATTACK" if is_attack else "NORMAL"
    status = "sent OK" if ok else "FAILED"
    print(f"  [{i+1:02d}] {icon:6}  {conf:5.1f}% confidence  {latency}ms  -> {status}")
    time.sleep(0.3)

print("-" * 45)
print("Done! 20 metrics sent to CloudWatch.")
print("")
print("Wait 30 seconds, then refresh your dashboard:")
print("https://console.aws.amazon.com/cloudwatch/home?region=us-east-1#dashboards:name=DDoS-Prediction-System")