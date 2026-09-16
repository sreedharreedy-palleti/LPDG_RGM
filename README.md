# LPDG Gateway Anomaly Detection Service

Automated decision engine that prioritizes the top 15 gateway field visits per week over the 8 scored evaluation weeks (120 visits total) based on radio network telemetry.

---

## 1. Project Background & Economics

* **Network Scale:** Around 320 radio gateways relaying meter telemetry across rooftop, basement, and plant room installations.
* **Failure Impact:** A silent gateway failure stops all meters behind it from being read.
* **Field Visit Cost:** Dispatching a technician costs **€380**.
* **Neglect Cost:** Leaving an undetected broken gateway ignored costs **€600 every week**.
* **Capacity Constraint:** The operations team has a strict capacity limit of **15 visits per week**.

---

## 2. Architecture & File Roles

* **`main.py` (The Engine Driver):** Starts the application. Reads paths from environment variables, verifies data availability via health check probes, drives the scoring pipeline, writes the output CSV, and asserts zero validation errors.
* **`model.py` (The Brain):** Calculates 28-day baseline distributions using Median Absolute Deviation (MAD) to detect 7-day deviations in `offline_duration_sec`, `disconnection_cnt`, and `reboot_cnt`. Applies metric weights and cascade penalties to rank the top 15 gateways per week with clear explanations under 300 characters.
* **`validate_submission.py` (The Rule Checker):** Verifies that `predictions.csv` strictly contains 120 rows, 5 exact columns, numeric scores, no duplicate gateways per week, ranks 1 to 15, and valid gateway ID formats.
* **`Dockerfile` & `docker-compose.yml` (The Box):** Packages the application into a minimal Python 3.11-slim container with automatic volume mounts, deep health checks, and unbuffered logging.
* **`tests/test_pipeline.py` (The Unit Tests):** Tests edge-case normalization for MAC IDs, empty CSV files, and missing required columns.
* **`DECISIONS.md` & `AI-USAGE.md` (The Explanations):** Details the 5 technical trade-offs made, model boundary limitations, and transparent disclosures regarding generative AI usage.

---

## 3. Evaluation & Execution Commands

### Step 1: Run the Pipeline (One-Command Start)

Run this command from the repository root:

```bash
docker compose up --build

What it verifies:

The Docker container builds successfully[cite: 12].

It finds and mounts the dataset from ./data.  

It executes the anomaly engine and writes ./output/predictions.csv.  

Step 2: Validate the Generated File
Run the grader script against the output:

Bash
python validate_submission.py output/predictions.csv

Expected terminal output:

Plaintext
output/predictions.csv: OK
  15 ranked gateways for each of 8 weeks, 2026-02-02 to 2026-03-23

Step 3: Run Local Unit Tests
Run the test suite with pytest:

Bash
pytest tests/ -v
Step 4: Verify Container Health Check
Check the runtime health probe status:

Bash
docker inspect --format='{{json .State.Health.Status}}' lpdg-service
Expected output: "healthy".  

Step 5: Check Container Logs
Inspect application logs directly from the container:

Bash
docker logs lpdg-service

4. Troubleshooting Checklist
Missing Data Error: Ensure parquet telemetry exists on the host at ./data/telemetry/month=YYYY-MM/*.parquet.  

Permission Denied on Output: Run mkdir -p output && chmod 777 output before starting the container.

Cleaning Artifacts: Run docker compose down -v to reset container state.

## 6. Walkthrough Video Demonstration

WWatch the complete 6–8 minute walkthrough demonstration:

👉 [Watch the Project Video Walkthrough](https://drive.google.com/drive/folders/1yWfunTacTGaAWMKt0S70mPlj0ghZn5aj)