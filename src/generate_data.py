"""
generate_data.py
================
Generates realistic multi-product, multi-location demand data
for a consumer electronics supply chain (inspired by peripherals/accessories).

Hierarchy:  Product Family → SKU → Region → Warehouse
Echelons:   Central DC  →  Regional DC  →  Local Warehouse

Output:     data/demand_history.csv
            data/network_config.csv
"""

import numpy as np
import pandas as pd
from pathlib import Path
from datetime import datetime, timedelta

np.random.seed(42)

# ── Configuration ──────────────────────────────────────────────
WEEKS = 104  # 2 years of weekly data
START_DATE = datetime(2023, 1, 2)  # First Monday of 2023

PRODUCTS = {
    "Wireless Mouse": {
        "SKUs": ["WM-PRO-BLK", "WM-PRO-WHT", "WM-LITE-GRY"],
        "base_demand": [120, 95, 200],
        "seasonality_amp": 0.25,        # holiday lift
        "trend": 0.001,                 # slight growth
        "noise_std": 0.15,
    },
    "Mechanical Keyboard": {
        "SKUs": ["KB-MX-TKL", "KB-MX-FULL", "KB-MEM-RGB"],
        "base_demand": [60, 45, 80],
        "seasonality_amp": 0.35,        # stronger holiday lift
        "trend": 0.002,
        "noise_std": 0.20,
    },
    "Webcam": {
        "SKUs": ["WC-HD-1080", "WC-4K-PRO"],
        "base_demand": [150, 55],
        "seasonality_amp": 0.15,
        "trend": -0.0005,               # slight decline post-pandemic
        "noise_std": 0.18,
    },
    "Headset": {
        "SKUs": ["HS-WIFI-PRO", "HS-BT-LITE", "HS-USB-STD"],
        "base_demand": [70, 130, 90],
        "seasonality_amp": 0.30,
        "trend": 0.0015,
        "noise_std": 0.16,
    },
}

REGIONS = {
    "EMEA": {
        "warehouses": ["Cork-IE", "Amsterdam-NL"],
        "demand_share": [0.45, 0.55],
    },
    "APAC": {
        "warehouses": ["Shanghai-CN", "Tokyo-JP"],
        "demand_share": [0.60, 0.40],
    },
    "Americas": {
        "warehouses": ["Louisville-US", "Toronto-CA"],
        "demand_share": [0.70, 0.30],
    },
}

# ── Network configuration (echelon structure) ─────────────────
NETWORK = {
    "Central_DC": {
        "name": "Global-HQ-DC",
        "echelon": 1,
        "lead_time_weeks": 0,
        "children": ["EMEA-RDC", "APAC-RDC", "Americas-RDC"],
    },
    "EMEA-RDC": {
        "name": "EMEA Regional DC",
        "echelon": 2,
        "lead_time_weeks": 2,
        "children": ["Cork-IE", "Amsterdam-NL"],
    },
    "APAC-RDC": {
        "name": "APAC Regional DC",
        "echelon": 2,
        "lead_time_weeks": 3,
        "children": ["Shanghai-CN", "Tokyo-JP"],
    },
    "Americas-RDC": {
        "name": "Americas Regional DC",
        "echelon": 2,
        "lead_time_weeks": 2,
        "children": ["Louisville-US", "Toronto-CA"],
    },
    "Cork-IE":       {"echelon": 3, "lead_time_weeks": 1, "children": []},
    "Amsterdam-NL":  {"echelon": 3, "lead_time_weeks": 1, "children": []},
    "Shanghai-CN":   {"echelon": 3, "lead_time_weeks": 1, "children": []},
    "Tokyo-JP":      {"echelon": 3, "lead_time_weeks": 1, "children": []},
    "Louisville-US": {"echelon": 3, "lead_time_weeks": 1, "children": []},
    "Toronto-CA":    {"echelon": 3, "lead_time_weeks": 1, "children": []},
}


def generate_seasonality(weeks: int) -> np.ndarray:
    """Multi-harmonic seasonality: holiday peak (Q4) + back-to-school (Q3)."""
    t = np.arange(weeks)
    annual = np.sin(2 * np.pi * (t - 13) / 52)      # peak ~ week 39 (Q4 ramp)
    biannual = 0.3 * np.sin(2 * np.pi * (t - 5) / 26)  # secondary lift
    return annual + biannual


def generate_demand():
    """Build the full demand history DataFrame."""
    seasonality = generate_seasonality(WEEKS)
    dates = [START_DATE + timedelta(weeks=w) for w in range(WEEKS)]
    rows = []

    for family, cfg in PRODUCTS.items():
        for i, sku in enumerate(cfg["SKUs"]):
            base = cfg["base_demand"][i]
            for region, rcfg in REGIONS.items():
                for j, wh in enumerate(rcfg["warehouses"]):
                    share = rcfg["demand_share"][j]
                    for w in range(WEEKS):
                        trend_factor = 1 + cfg["trend"] * w
                        season_factor = 1 + cfg["seasonality_amp"] * seasonality[w]
                        noise = np.random.lognormal(0, cfg["noise_std"])
                        demand = max(0, round(
                            base * share * trend_factor * season_factor * noise
                        ))
                        rows.append({
                            "date": dates[w],
                            "week_num": w + 1,
                            "product_family": family,
                            "sku": sku,
                            "region": region,
                            "warehouse": wh,
                            "demand_units": demand,
                        })

    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"])
    return df


def generate_network_config():
    """Flatten network config into a DataFrame for reference."""
    rows = []
    for node_id, info in NETWORK.items():
        rows.append({
            "node_id": node_id,
            "name": info.get("name", node_id),
            "echelon": info["echelon"],
            "lead_time_weeks": info["lead_time_weeks"],
            "children": ", ".join(info["children"]) if info["children"] else "",
        })
    return pd.DataFrame(rows)


if __name__ == "__main__":
    out_dir = Path(__file__).resolve().parent.parent / "data"
    out_dir.mkdir(exist_ok=True)

    # Demand history
    demand = generate_demand()
    demand.to_csv(out_dir / "demand_history.csv", index=False)
    print(f"✓ demand_history.csv  — {len(demand):,} rows, "
          f"{demand['sku'].nunique()} SKUs × {demand['warehouse'].nunique()} warehouses × {WEEKS} weeks")

    # Network config
    net = generate_network_config()
    net.to_csv(out_dir / "network_config.csv", index=False)
    print(f"✓ network_config.csv  — {len(net)} nodes across 3 echelons")

    # Quick summary stats
    print("\n── Demand Summary ──")
    print(demand.groupby("product_family")["demand_units"].describe()
          .round(1)[["mean", "std", "min", "max"]])
