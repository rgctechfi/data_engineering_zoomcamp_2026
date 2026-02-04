"""Ingest NYC taxi parquet files into GCS.

This script downloads NYC Yellow Taxi parquet files from a public endpoint and
uploads them to a Google Cloud Storage bucket. It reads the GCP project ID and
bucket name from a Terraform tfvars file, with optional CLI overrides.

Prerequisites:
1) GCP authentication is configured via GOOGLE_APPLICATION_CREDENTIALS or gcloud.
2) The target bucket exists and the service account has write permissions.

Examples:
    python Homeworks/3_BigQuery/ingest.py
    python Homeworks/3_BigQuery/ingest.py --months 01,02,03
    python Homeworks/3_BigQuery/ingest.py --project my-project --bucket my-bucket
"""

import argparse  # argparse: standard library module for parsing CLI arguments.
import os

# requests: HTTP client for downloading files from the public dataset endpoint.
import requests
# google.cloud.storage: official GCP SDK for uploading files to GCS.
from google.cloud import storage
# HTTPAdapter + Retry: add automatic retries for transient HTTP errors.
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

# Base URL hosting NYC taxi parquet files.
BASE_URL = "https://d37ci6vzurychx.cloudfront.net/trip-data"
# Default time window for the homework (Jan–Jun 2024).
DEFAULT_YEAR = "2024"
DEFAULT_MONTHS = [f"{i:02d}" for i in range(1, 7)]  # Jan to Jun
# Default path to Terraform variables (source of project/bucket values) -> if we are at the root of the projet!
DEFAULT_TFVARS = "Module_1_Terraform/dev/terraform.tfvars"


def parse_tfvars(path):
    """Parse a simple terraform.tfvars file with key = "value" lines."""
    config = {}
    if not os.path.exists(path):
        return config

    with open(path, "r", encoding="utf-8") as tfvars:
        for raw_line in tfvars:
            line = raw_line.strip()
            if not line or line.startswith("#") or line.startswith("//"):
                continue
            for token in ("#", "//"):
                if token in line:
                    line = line.split(token, 1)[0].strip()
            if not line or "=" not in line:
                continue
            key, value = line.split("=", 1)
            key = key.strip()
            value = value.strip().strip('"').strip("'")
            if key:
                config[key] = value
    return config


def parse_months(months_text):
    """Convert a comma-separated list of months into ["01", "02", ...]."""
    if not months_text:
        return DEFAULT_MONTHS

    months = []
    for part in months_text.split(","):
        token = part.strip()
        if not token:
            continue
        try:
            month_num = int(token)
        except ValueError as exc:
            raise ValueError(f"Invalid month: {token}") from exc
        if month_num < 1 or month_num > 12:
            raise ValueError(f"Invalid month: {token}")
        months.append(f"{month_num:02d}")

    if not months:
        raise ValueError("No valid month provided.")

    return months


def create_session():
    """Create a requests session with light retry logic for robustness."""
    retry = Retry(
        total=3,
        backoff_factor=0.5,
        status_forcelist=(429, 500, 502, 503, 504),
        allowed_methods=("GET",),
    )
    adapter = HTTPAdapter(max_retries=retry)
    session = requests.Session()
    session.mount("https://", adapter)
    session.mount("http://", adapter)
    return session


def download_file(session, url, destination, timeout=30):
    """Stream-download a file to disk; return False if 404 (missing month)."""
    with session.get(url, stream=True, timeout=timeout) as response:
        if response.status_code == 404:
            return False
        if response.status_code != 200:
            response.raise_for_status()
        with open(destination, "wb") as target:
            for chunk in response.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    target.write(chunk)
    return True


def upload_to_gcs(bucket, source_file_name, destination_blob_name):
    """Upload a local file to a destination path in a GCS bucket."""
    blob = bucket.blob(destination_blob_name)
    blob.upload_from_filename(source_file_name)
    print(f"File {source_file_name} uploaded to {destination_blob_name}.")


def get_bucket_or_exit(project_id, bucket_name):
    """Return a GCS bucket object or exit if the bucket does not exist."""
    storage_client = storage.Client(project=project_id)
    bucket = storage_client.lookup_bucket(bucket_name)
    if bucket is None:
        raise SystemExit(
            f"Bucket not found: {bucket_name}. "
            "Make sure it exists and you are using the correct GCP project."
        )
    return bucket


def resolve_config(args):
    """Resolve project/bucket/year/months from tfvars + CLI overrides."""
    tfvars = parse_tfvars(args.tfvars)
    project_id = args.project or tfvars.get("project")
    bucket_name = args.bucket or tfvars.get("gcs_bucket_name")

    if not project_id:
        raise ValueError(
            "Missing Project ID. Provide --project or set 'project' in terraform.tfvars."
        )
    if not bucket_name:
        raise ValueError(
            "Missing bucket. Provide --bucket or set 'gcs_bucket_name' in terraform.tfvars."
        )

    months = parse_months(args.months)
    year = args.year

    return project_id, bucket_name, year, months


def main():
    """CLI entrypoint: download taxi files and upload them to GCS."""
    parser = argparse.ArgumentParser(description="Ingestion NYC Taxi -> GCS")
    parser.add_argument("--tfvars", default=DEFAULT_TFVARS, help="Path to terraform.tfvars")
    parser.add_argument("--project", help="Override Project ID")
    parser.add_argument("--bucket", help="Override GCS bucket")
    parser.add_argument("--year", default=DEFAULT_YEAR, help="Data year")
    parser.add_argument(
        "--months",
        help="Comma-separated months, e.g. 01,02,03",
    )
    args = parser.parse_args()

    try:
        project_id, bucket_name, year, months = resolve_config(args)
    except ValueError as exc:
        raise SystemExit(str(exc)) from exc

    session = create_session()
    bucket = get_bucket_or_exit(project_id, bucket_name)
    uploaded_count = 0
    skipped_count = 0
    missing_count = 0

    for month in months:
        file_name = f"yellow_tripdata_{year}-{month}.parquet"
        request_url = f"{BASE_URL}/{file_name}"
        destination_blob_name = f"raw/ny_taxi/{file_name}"

        # Check if the object already exists in GCS to avoid re-downloading.
        blob = bucket.blob(destination_blob_name)
        if blob.exists():
            print(f"Already in GCS, skipping: {destination_blob_name}")
            skipped_count += 1
            continue

        print(f"Download: {request_url}")

        try:
            available = download_file(session, request_url, file_name)
        except requests.RequestException as exc:
            print(f"Download failed for month {month}: {exc}")
            continue

        if not available:
            print(f"No data available for month {month}")
            missing_count += 1
            continue

        # Upload the local file into the target GCS prefix.
        upload_to_gcs(bucket, file_name, destination_blob_name)
        uploaded_count += 1
        os.remove(file_name)

    print(
        "Summary -> uploaded: "
        f"{uploaded_count}, already present: {skipped_count}, missing: {missing_count}"
    )


if __name__ == "__main__":
    main()
