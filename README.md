# LPDG Anomaly Detection Service

Production service for detecting telemetry anomalies and ranking gateway site visits.

---

## 1. How to Run

### Prerequisites
* Docker and Docker Compose installed on your system.
* Telemetry parquet dataset placed inside `./data/telemetry`.

### One-Command Start
Run the following command in the repository root:

```bash
docker compose up --build