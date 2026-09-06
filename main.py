import os
import sys
import logging
import pathlib
import datetime as dt
import pandas as pd
from baseline_3sigma import load, build_predictions
from validate_submission import validate

# Setup structured logging
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("lpdg-service")

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "./data"))
OUTPUT_PATH = pathlib.Path(os.getenv("OUTPUT_PATH", "./predictions.csv"))

def run_healthcheck() -> int:
    logger.info("Starting health check...")
    # Verify critical paths and data accessibility
    telemetry_dir = DATA_DIR / "telemetry"
    if not telemetry_dir.exists():
        logger.error("Health check FAILED: Missing telemetry directory at %s", telemetry_dir)
        return 1

    try:
        # Check if parquet data can actually be read
        test_df = pd.read_parquet(telemetry_dir)
        if test_df.empty:
            logger.error("Health check FAILED: Telemetry data is empty.")
            return 1
        logger.info("Health check PASSED: Found %d telemetry records.", len(test_df))
        return 0
    except Exception as exc:
        logger.error("Health check FAILED with error: %s", exc)
        return 1

def run_pipeline() -> int:
    logger.info("Launching prediction pipeline...")
    logger.info("Reading telemetry from %s", DATA_DIR)
    
    frame = load(DATA_DIR)
    predictions = build_predictions(frame)
    predictions.to_csv(OUTPUT_PATH, index=False)
    logger.info("Predictions saved to %s", OUTPUT_PATH)

    # Self-validation check
    problems = validate(OUTPUT_PATH)
    if problems:
        logger.error("Submission failed validation with %d issues:", len(problems))
        for p in problems:
            logger.error("  - %s", p)
        return 1

    logger.info("Pipeline executed successfully and generated valid predictions!")
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--healthcheck":
        sys.exit(run_healthcheck())
    sys.exit(run_pipeline())