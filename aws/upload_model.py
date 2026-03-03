"""
aws/upload_model.py
--------------------
Uploads the trained AdaBoost model to AWS S3.

In a real production system, the model lives in S3 — not on local disk.
This means:
  - Any server, container, or Lambda function can load the latest model
  - You can version models (v1, v2, v3) and roll back instantly
  - The model is backed up and never lost if a server dies

AWS Free Tier: S3 gives you 5GB storage free for 12 months.

Setup (one time):
    1. Create a free AWS account at aws.amazon.com
    2. Go to IAM → create a user with S3 + CloudWatch permissions
    3. Run: aws configure   (enter your Access Key ID and Secret)

Usage:
    python aws/upload_model.py
"""

import os
import sys
import json

# boto3 is the official AWS SDK for Python
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError
except ImportError:
    print("boto3 not installed. Run: pip install boto3")
    sys.exit(1)

# ─── Config ───────────────────────────────────────────────────────────────────
BUCKET_NAME  = "ddos-prediction-model"   # change to your unique bucket name
REGION       = "us-east-1"               # AWS Free Tier region
MODEL_DIR    = os.path.join(os.path.dirname(__file__), "..", "models")

FILES_TO_UPLOAD = [
    "adaboost.pkl",
    "scaler.pkl",
    "feature_cols.json",
    "results_summary.json",
]

def create_bucket_if_not_exists(s3, bucket_name, region):
    """Create the S3 bucket if it doesn't already exist."""
    try:
        s3.head_bucket(Bucket=bucket_name)
        print(f"  Bucket '{bucket_name}' already exists")
    except ClientError as e:
        error_code = e.response["Error"]["Code"]
        if error_code == "404":
            print(f"  Creating bucket '{bucket_name}'...")
            if region == "us-east-1":
                s3.create_bucket(Bucket=bucket_name)
            else:
                s3.create_bucket(
                    Bucket=bucket_name,
                    CreateBucketConfiguration={"LocationConstraint": region}
                )
            print(f"  Bucket created successfully")
        else:
            raise

def upload_models(bucket_name=BUCKET_NAME, region=REGION):
    """Upload all model artifacts to S3."""
    print("\n" + "="*55)
    print("  Uploading Model Artifacts to AWS S3")
    print("="*55)

    try:
        s3 = boto3.client("s3", region_name=region)

        # Verify credentials work
        s3.list_buckets()
        print(f"\n  AWS credentials verified ✓")
        print(f"  Region: {region}")

        create_bucket_if_not_exists(s3, bucket_name, region)

        print(f"\n  Uploading files to s3://{bucket_name}/")
        uploaded = []
        for filename in FILES_TO_UPLOAD:
            local_path = os.path.join(MODEL_DIR, filename)
            if not os.path.exists(local_path):
                print(f"  ⚠ Skipping {filename} — file not found")
                continue

            s3_key = f"models/{filename}"
            file_size = os.path.getsize(local_path)

            s3.upload_file(local_path, bucket_name, s3_key)
            print(f"  ✓ {filename} → s3://{bucket_name}/{s3_key} ({file_size:,} bytes)")
            uploaded.append(s3_key)

        # Save a manifest so we know what's in the bucket
        manifest = {
            "uploaded_files": uploaded,
            "bucket": bucket_name,
            "region": region,
            "model": "AdaBoostClassifier",
            "description": "DDoS Attack Prediction System — trained model artifacts",
        }
        s3.put_object(
            Bucket=bucket_name,
            Key="models/manifest.json",
            Body=json.dumps(manifest, indent=2),
            ContentType="application/json"
        )

        print(f"\n  Upload complete!")
        print(f"  View in AWS Console:")
        print(f"  https://s3.console.aws.amazon.com/s3/buckets/{bucket_name}")
        print("="*55 + "\n")
        return True

    except NoCredentialsError:
        print("\n  ✗ AWS credentials not found.")
        print("  Run 'aws configure' and enter your Access Key ID and Secret.")
        print("  Get credentials from: AWS Console → IAM → Users → Security Credentials")
        return False
    except Exception as e:
        print(f"\n  ✗ Error: {e}")
        return False


def load_model_from_s3(bucket_name=BUCKET_NAME, region=REGION):
    """
    Downloads the model from S3 and loads it into memory.
    This is how the production Flask API would load its model.
    """
    import pickle
    import io

    s3 = boto3.client("s3", region_name=region)

    print("  Loading model from S3...")
    obj = s3.get_object(Bucket=bucket_name, Key="models/adaboost.pkl")
    model = pickle.load(io.BytesIO(obj["Body"].read()))

    obj = s3.get_object(Bucket=bucket_name, Key="models/scaler.pkl")
    scaler = pickle.load(io.BytesIO(obj["Body"].read()))

    obj = s3.get_object(Bucket=bucket_name, Key="models/feature_cols.json")
    features = json.loads(obj["Body"].read().decode("utf-8"))

    print(f"  Model loaded from S3 — {len(features)} features ✓")
    return model, scaler, features


if __name__ == "__main__":
    upload_models()
