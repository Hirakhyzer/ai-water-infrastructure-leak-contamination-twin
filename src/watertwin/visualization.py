"""Plotting helpers for local synthetic water digital twin outputs."""

from __future__ import annotations

from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd


def _save(fig, path: str | Path) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    fig.tight_layout()
    fig.savefig(path, dpi=160)
    plt.close(fig)


def plot_anomaly_scores(scores: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    scores["overall_response_risk_score"].plot(kind="hist", bins=12, ax=ax)
    ax.set_title("Overall water-infrastructure anomaly risk")
    ax.set_xlabel("Risk score")
    _save(fig, path)


def plot_zone_risk(priority: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    priority.groupby("zone_id")["response_priority_score"].max().sort_values(ascending=False).head(12).plot(kind="bar", ax=ax)
    ax.set_title("Highest zone response priorities")
    ax.set_xlabel("Zone")
    ax.set_ylabel("Priority score")
    _save(fig, path)


def plot_quality_shift(scores: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    scores["water_quality_shift_score"].plot(kind="hist", bins=12, ax=ax)
    ax.set_title("Water-quality shift score distribution")
    ax.set_xlabel("Quality shift score")
    _save(fig, path)


def plot_robustness(robustness: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    robustness.groupby("stressor")["mean_score_degradation"].max().sort_values(ascending=False).plot(kind="bar", ax=ax)
    ax.set_title("Worst score degradation by sensor stressor")
    ax.set_ylabel("Mean score degradation")
    ax.tick_params(axis="x", rotation=25)
    _save(fig, path)


def plot_evaluation(metrics: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    metrics.set_index("task")["f1"].plot(kind="bar", ax=ax)
    ax.set_title("Synthetic detector F1 by task")
    ax.set_ylim(0, 1)
    _save(fig, path)


def plot_priority_bands(priority: pd.DataFrame, path: str | Path) -> None:
    fig, ax = plt.subplots(figsize=(8, 4.5))
    priority["priority_band"].value_counts().reindex(["routine", "elevated", "urgent", "critical"]).fillna(0).plot(kind="bar", ax=ax)
    ax.set_title("Response priority bands")
    ax.set_xlabel("Priority band")
    ax.set_ylabel("Sensor count")
    _save(fig, path)
