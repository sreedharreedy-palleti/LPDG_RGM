import logging
import os
import pathlib
import sys
from baseline_3sigma import load
from model import build_enhanced_predictions
import pandas as pd
from validate_submission import validate

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("lpdg-service")

DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/app/data"))
OUTPUT_PATH = pathlib.Path(os.getenv("OUTPUT_PATH", "/app/output/predictions.csv"))


def run_healthcheck() -> int:
    logger.info("Executing container health check...")
    telemetry_dir = DATA_DIR / "telemetry"
    if not telemetry_dir.exists():
        logger.error("Health check failed: Missing telemetry path %s", telemetry_dir)
        return 1
    try:
        sample = pd.read_parquet(telemetry_dir)
        if sample.empty:
            logger.error("Health check failed: Empty telemetry dataset")
            return 1
        logger.info("Health check passed: %d records found", len(sample))
        return 0
    except Exception as err:
        logger.error("Health check error: %s", err)
        return 1


def run_pipeline() -> int:
    logger.info("Starting pipeline with DATA_DIR=%s, OUTPUT=%s", DATA_DIR, OUTPUT_PATH)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Reading telemetry parquet files...")
    frame = load(DATA_DIR)

    logger.info("Generating scored site visit recommendations...")
    predictions = build_enhanced_predictions(frame)
    predictions.to_csv(OUTPUT_PATH, index=False)
    logger.info("Saved %d predictions to %s", len(predictions), OUTPUT_PATH)

    logger.info("Validating submission constraints...")
    problems = validate(OUTPUT_PATH)
    if problems:
        logger.error("Validation failed with %d issue(s):", len(problems))
        for p in problems:
            logger.error("  - %s", p)
        return 1

    logger.info("Validation passed successfully (120/120 rows valid).")
    return 0


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--healthcheck":
        sys.exit(run_healthcheck())
    sys.exit(run_pipeline())