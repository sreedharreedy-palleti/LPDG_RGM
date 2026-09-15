# AI Usage Disclosure

### What AI Tools Were Used
* **Docker & Environment Scaffolding:** Used LLM assistance to generate boilerplate for `Dockerfile` multi-stage patterns and the `docker-compose.yml` health-check configuration.
* **Unit Testing Edge Cases:** Generated synthetic test cases in `test_pipeline.py` verifying MAC address normalization regexes and edge formatting conditions.
* **Vectorized Pandas Refactoring:** Consulted AI to optimize rolling window aggregations over multi-gigabyte parquet partitions.

### What AI Got Wrong & How It Was Caught
* **The Error:** An AI suggestion attempted to generate rolling window slices using `pd.Timedelta(days=28)` inside index lookups on a DatetimeIndex with mixed timezone definitions, and suggested parsing gateway IDs into standard integers.
* **Why It Broke:** `pd.Timedelta` with NumPy 2.x emitted deprecation warnings, and converting gateway MAC addresses (`001122334455`) to integers stripped critical leading zeros (e.g., converting `0011...` into a shorter number), breaking submission format requirements.
* **Correction:** Retained standard ISO-8601 strings and bare hexadecimal upper-casing using regex matching in line with `validate_submission.py`.