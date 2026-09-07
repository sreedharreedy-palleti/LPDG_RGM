import os
import sys
import logging
import pathlib
import pandas as pd
from baseline_3sigma import load, build_predictions
from validate_submission import validate

# 1. Structured logs worth reading
logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("lpdg-service")

# 2. Settings from environment (no laptop paths)
DATA_DIR = pathlib.Path(os.getenv("DATA_DIR", "/app/data"))
OUTPUT_PATH = pathlib.Path(os.getenv("OUTPUT_PATH", "/app/output/predictions.csv"))

def run_healthcheck() -> int:
    """Active health check: fails if telemetry directory or parquet files are unreadable."""
    logger.info("Executing deep health check...")
    telemetry_dir = DATA_DIR / "telemetry"
    if not telemetry_dir.exists():
        logger.error("Health check failed: Missing telemetry folder at %s", telemetry_dir)
        return 1

    try:
        sample = pd.read_parquet(telemetry_dir)
        if sample.empty:
            logger.error("Health check failed: Telemetry table is empty")
            return 1
        logger.info("Health check passed: Telemetry dataset is accessible (%d rows)", len(sample))
        return 0
    except Exception as err:
        logger.error("Health check failed with error: %s", err)
        return 1

def run_pipeline() -> int:
    logger.info("Pipeline started with DATA_DIR=%s and OUTPUT_PATH=%s", DATA_DIR, OUTPUT_PATH)
    
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    logger.info("Loading telemetry dataset...")
    frame = load(DATA_DIR)
    
    logger.info("Computing 3-sigma anomaly baselines...")
    predictions = build_predictions(frame)
    predictions.to_csv(OUTPUT_PATH, index=False)
    logger.info("Predictions written to %s (%d rows)", OUTPUT_PATH, len(predictions))

    logger.info("Running submission validator...")
    problems = validate(OUTPUT_PATH)
    if problems:
        logger.error("Validation failed with %d problem(s):", len(problems))
        for p in problems:
            logger.error("  - %s", p)
        return 1

    logger.info("Pipeline finished successfully with 0 validation errors.")
    return 0

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "--healthcheck":
        sys.exit(run_healthcheck())
    sys.exit(run_pipeline())