# Architectural & Modeling Decisions

### Decision 1: Robust Rolling Scaling (Median / MAD) vs. Gaussian 3-Sigma
* **Choice:** Replaced standard arithmetic mean and sample standard deviation with Median and Median Absolute Deviation (MAD) over a trailing 28-day baseline.
* **Alternative Considered:** Fixed Gaussian 3-sigma thresholds (`mean + 3 * std`).
* **Rationale:** Gateway telemetry distributions for disconnections and reboot counts are heavily zero-inflated and right-skewed. Outliers in standard deviation inflate the denominator, which causes subsequent persistent anomalies to go undetected. MAD ensures robust scaling invariant to extreme past spikes.

### Decision 2: Multi-Metric Weighted Severity Scoring vs. Simple Breach Counting
* **Choice:** Weighted sum of deviations where `reboot_cnt` has highest weight (2.0x), followed by `offline_duration_sec` (1.5x) and `disconnection_cnt` (1.0x), plus a compound instability penalty for concurrent disconnections and reboots.
* **Alternative Considered:** Unweighted discrete breach counts (1 count per hour threshold exceeded).
* **Rationale:** An unweighted hour count treats a minor 1-second drop identical to a gateway trapped in a hard boot loop. Weighting captures the operational impact of field hardware failure.

### Decision 3: Part 2 Specialization Track
* **Choice:** Selected **Track A: Operational Edge Anomaly Detection & Predictive Maintenance**.
* **Rationale:** Preventing redundant physical technician dispatches provides immediate operational cost savings. Prioritizing gateways caught in hardware-level boot cascades maximizes visit effectiveness over transient carrier-level disconnects.

### Decision 4: Cold-Start & Zero-Variance Gateway Handling
* **Choice:** Fallback scaling that defaults zero-variance denominators to unit scale (1.0) and fills unflagged slots with baseline routine maintenance rank ordering.
* **Alternative Considered:** Dropping gateways with insufficient history or zero variance.
* **Rationale:** The grader mandates strictly 15 ranked gateways per scored week (120 rows total). Zero-variance gateways would crash standard division (`x / 0`) or lead to underfilled prediction tables.

### Decision 5: File-Based Containerized Batch Pipeline vs. Persistent Microservice
* **Choice:** Single-command Docker container batch execution writing directly to an output volume with built-in validation.
* **Alternative Considered:** A long-running FastAPI/REST microservice with PostgreSQL telemetry caching.
* **Rationale:** A containerized CLI batch pipeline guarantees idempotency, zero overhead, and native integration into automated evaluation harnesses without external database networking dependencies.

---

## What It Cannot Do

* **Fleet-Wide Outage Differentiation:** If an entire regional ISP goes down, dozens of gateways will exhibit simultaneous telemetry spikes. The current model scores them individually and may allocate all 15 technician visits to one localized external network blackout.
* **Predictive Pre-Failure Lead Time:** The model detects existing degradation patterns in trailing telemetry; it does not forecast future wear on power supplies before telemetry degradation begins.

### Two-Week Roadmap
1. **Spatial & Topology Clustering (DBSCAN):** Group co-located gateways to suppress technician dispatches when multiple adjacent units drop at the exact same hour (isolating ISP/grid issues from hardware faults).
2. **Survival Analysis / Weibull Degradation Modeling:** Estimate mean time to failure (MTTF) for gateways displaying intermittent reboot trends.