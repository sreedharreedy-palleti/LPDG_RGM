"""Enhanced Anomaly Detection and Site Visit Prioritization Model."""

from __future__ import annotations

import datetime as dt
import numpy as np
import pandas as pd
from validate_submission import MAX_REASON_CHARS, SCORED_WEEKS, VISITS_PER_WEEK

METRICS = ["offline_duration_sec", "disconnection_cnt", "reboot_cnt"]
METRIC_WEIGHTS = {
    "offline_duration_sec": 1.5,
    "disconnection_cnt": 1.0,
    "reboot_cnt": 2.0,
}
BASELINE_DAYS = 28
RECENT_DAYS = 7


def compute_mad(series: pd.Series) -> float:
    """Compute Median Absolute Deviation (MAD) for robust outlier scaling."""
    med = series.median()
    mad = (series - med).abs().median()
    return float(1.4826 * mad) if mad > 0 else float(series.std(ddof=0) or 1.0)


def rank_week_enhanced(frame: pd.DataFrame, monday: dt.date) -> pd.DataFrame:
    end = pd.Timestamp(monday, tz="UTC")
    baseline_start = end - dt.timedelta(days=BASELINE_DAYS)
    recent_start = end - dt.timedelta(days=RECENT_DAYS)

    window = frame[(frame["ts"] >= baseline_start) & (frame["ts"] < end)]
    if window.empty:
        return pd.DataFrame(columns=["gateway_id", "score", "reason"])

    recent = window[window["ts"] >= recent_start].copy()
    if recent.empty:
        return pd.DataFrame(columns=["gateway_id", "score", "reason"])

    scores_per_gw: dict[str, float] = {}
    reasons_per_gw: dict[str, str] = {}

    for gw_id, gw_group in window.groupby("gateway_id"):
        recent_gw = recent[recent["gateway_id"] == gw_id]
        if recent_gw.empty:
            continue

        total_gw_score = 0.0
        primary_drivers = []

        for metric in METRICS:
            hist_vals = gw_group[metric]
            hist_median = hist_vals.median()
            scale = compute_mad(hist_vals)

            recent_vals = recent_gw[metric]
            z_robust = (recent_vals - hist_median) / scale
            outliers = z_robust[z_robust > 3.0]

            if not outliers.empty:
                weighted_contribution = float(outliers.sum() * METRIC_WEIGHTS[metric])
                total_gw_score += weighted_contribution
                primary_drivers.append(
                    f"{len(outliers)}x {metric} spike (max {recent_vals.max():.0f})"
                )

        # Compound penalty: frequent reboots while suffering disconnections
        compound_penalty = float(
            ((recent_gw["reboot_cnt"] > 0) & (recent_gw["disconnection_cnt"] > 2)).sum()
        ) * 5.0
        total_gw_score += compound_penalty

        if compound_penalty > 0:
            primary_drivers.append(f"{int(compound_penalty / 5.0)} instability cascades")

        scores_per_gw[gw_id] = round(total_gw_score, 2)
        if primary_drivers:
            reason = "; ".join(primary_drivers)
            if len(reason) > (MAX_REASON_CHARS - 35):
                reason = reason[: MAX_REASON_CHARS - 38] + "..."
            reasons_per_gw[gw_id] = (
                f"Elevated risk (score: {total_gw_score:.1f}): {reason}"
            )
        else:
            reasons_per_gw[gw_id] = (
                "Routine baseline inspection; nominal metrics within normal variance"
            )

    ranked_df = pd.DataFrame(
        [
            {"gateway_id": gid, "score": scores_per_gw[gid], "reason": reasons_per_gw[gid]}
            for gid in scores_per_gw
        ]
    )

    ranked_df = ranked_df.sort_values("score", ascending=False).reset_index(drop=True)
    return ranked_df


def build_enhanced_predictions(frame: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for monday in SCORED_WEEKS:
        ranked = rank_week_enhanced(frame, monday)
        if len(ranked) < VISITS_PER_WEEK:
            raise SystemExit(f"Not enough gateways with telemetry before {monday}")

        top_visits = ranked.head(VISITS_PER_WEEK)
        for rank_num, row in enumerate(top_visits.itertuples(index=False), 1):
            rows.append(
                {
                    "week_start": monday.isoformat(),
                    "rank": rank_num,
                    "gateway_id": row.gateway_id,
                    "score": float(row.score),
                    "reason": row.reason,
                }
            )
    return pd.DataFrame(rows)