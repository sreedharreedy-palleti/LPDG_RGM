# LPDG Anomaly Detection Service

Production service for detecting telemetry anomalies and ranking gateway site visits. It ingests hourly telemetry, prioritizes the 15 gateways most in need of inspection for each of the 8 scored weeks, and writes schema-compliant predictions.

---

## 1. How to Run

### Prerequisites
* Docker and Docker Compose installed on your system.
* Telemetry parquet dataset placed inside `./data/telemetry`.

### One-Command Start
Run the following command in the repository root:

```bash
docker compose up --build