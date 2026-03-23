"""
inventory_opt.py
================
Multi-Echelon Inventory Optimisation comparing:
  1. Heuristic (RQ) policy — simple reorder-point / order-quantity
  2. Optimisation-based (base-stock) policy — service-level driven
  3. Multi-echelon guaranteed-service model (simplified Clark-Scarf)

Trade-off analysis: Service Level vs Holding Cost
"""

import numpy as np
import pandas as pd
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional
from scipy import stats
from pathlib import Path


# ── Data containers ────────────────────────────────────────────
@dataclass
class InventoryNode:
    node_id: str
    echelon: int
    lead_time_weeks: int
    holding_cost_per_unit: float
    children: List[str] = field(default_factory=list)
    demand_mean: float = 0.0
    demand_std: float = 0.0


@dataclass
class PolicyResult:
    policy_name: str
    node_id: str
    sku: str
    reorder_point: float
    order_quantity: float
    safety_stock: float
    avg_inventory: float
    holding_cost_weekly: float
    service_level: float
    fill_rate: float
    stockout_probability: float

    def to_dict(self) -> dict:
        return {
            "policy": self.policy_name,
            "node": self.node_id,
            "sku": self.sku,
            "reorder_point": round(self.reorder_point, 1),
            "order_qty": round(self.order_quantity, 1),
            "safety_stock": round(self.safety_stock, 1),
            "avg_inventory": round(self.avg_inventory, 1),
            "holding_cost_wk": round(self.holding_cost_weekly, 2),
            "service_level_%": round(self.service_level * 100, 1),
            "fill_rate_%": round(self.fill_rate * 100, 1),
            "stockout_prob_%": round(self.stockout_probability * 100, 2),
        }


# ── Holding cost assumptions (per unit per week) ──────────────
HOLDING_COSTS = {
    1: 0.05,   # Central DC — cheapest
    2: 0.12,   # Regional DC
    3: 0.20,   # Local warehouse — most expensive
}


# ── Policy 1: (R, Q) Heuristic ────────────────────────────────
class RQHeuristic:
    """
    Traditional Reorder Point / Order Quantity policy.
    R = mean demand over lead time + z * std over lead time
    Q = Economic Order Quantity (EOQ)
    """

    def __init__(self, ordering_cost: float = 50.0):
        self.ordering_cost = ordering_cost

    def compute(
        self,
        node: InventoryNode,
        sku: str,
        target_service_level: float = 0.95,
    ) -> PolicyResult:
        mu_L = node.demand_mean * node.lead_time_weeks
        sigma_L = node.demand_std * np.sqrt(node.lead_time_weeks)

        z = stats.norm.ppf(target_service_level)
        safety_stock = z * sigma_L
        reorder_point = mu_L + safety_stock

        # EOQ
        D_annual = node.demand_mean * 52
        h = node.holding_cost_per_unit
        Q = np.sqrt(2 * D_annual * self.ordering_cost / max(h, 0.01))
        Q = max(Q, 1)

        # Performance metrics
        avg_inventory = Q / 2 + safety_stock
        holding_cost = avg_inventory * h

        # Expected stockout
        stockout_prob = 1 - stats.norm.cdf(z)

        # Type-2 service level (fill rate)
        loss_fn = sigma_L * (stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z)))
        fill_rate = 1 - loss_fn / Q if Q > 0 else 0

        return PolicyResult(
            policy_name="(R,Q) Heuristic",
            node_id=node.node_id,
            sku=sku,
            reorder_point=reorder_point,
            order_quantity=Q,
            safety_stock=safety_stock,
            avg_inventory=avg_inventory,
            holding_cost_weekly=holding_cost,
            service_level=target_service_level,
            fill_rate=min(fill_rate, 1.0),
            stockout_probability=stockout_prob,
        )


# ── Policy 2: Base-Stock (Order-Up-To) ────────────────────────
class BaseStockPolicy:
    """
    Base-stock / order-up-to policy.
    S = mean demand over (lead time + review period) + z * std
    Optimal for single-echelon under normal demand.
    """

    def __init__(self, review_period: int = 1):
        self.review_period = review_period  # weeks

    def compute(
        self,
        node: InventoryNode,
        sku: str,
        target_service_level: float = 0.95,
    ) -> PolicyResult:
        protection_period = node.lead_time_weeks + self.review_period
        mu_P = node.demand_mean * protection_period
        sigma_P = node.demand_std * np.sqrt(protection_period)

        z = stats.norm.ppf(target_service_level)
        base_stock = mu_P + z * sigma_P
        safety_stock = z * sigma_P

        # Average inventory ≈ safety stock + review_period * mean / 2
        avg_inventory = safety_stock + self.review_period * node.demand_mean / 2
        holding_cost = avg_inventory * node.holding_cost_per_unit

        stockout_prob = 1 - stats.norm.cdf(z)

        # Fill rate
        loss_fn = sigma_P * (stats.norm.pdf(z) - z * (1 - stats.norm.cdf(z)))
        Q_equiv = node.demand_mean * self.review_period
        fill_rate = 1 - loss_fn / max(Q_equiv, 1)

        return PolicyResult(
            policy_name="Base-Stock (S)",
            node_id=node.node_id,
            sku=sku,
            reorder_point=base_stock,
            order_quantity=Q_equiv,
            safety_stock=safety_stock,
            avg_inventory=avg_inventory,
            holding_cost_weekly=holding_cost,
            service_level=target_service_level,
            fill_rate=min(fill_rate, 1.0),
            stockout_probability=stockout_prob,
        )


# ── Policy 3: Multi-Echelon Guaranteed Service (simplified) ───
class MultiEchelonGSM:
    """
    Simplified Guaranteed-Service Model (GSM) for multi-echelon networks.
    Each node commits to a service time (guaranteed outbound lead time).
    Safety stock = z * σ * √(net_lead_time)
    where net_lead_time = max(0, inbound_LT + processing_LT - committed_service_time)
    """

    def __init__(self, committed_service_times: Optional[Dict[str, int]] = None):
        self.committed_service = committed_service_times or {}

    def compute(
        self,
        node: InventoryNode,
        sku: str,
        target_service_level: float = 0.95,
        parent_service_time: int = 0,
    ) -> PolicyResult:
        # Inbound lead time = parent's committed service time + own lead time
        inbound_lt = parent_service_time + node.lead_time_weeks
        committed_st = self.committed_service.get(node.node_id, 0)
        net_lt = max(0, inbound_lt - committed_st)

        z = stats.norm.ppf(target_service_level)
        sigma_net = node.demand_std * np.sqrt(max(net_lt, 0.5))
        safety_stock = z * sigma_net

        avg_inventory = safety_stock + node.demand_mean * 0.5  # half-period average
        holding_cost = avg_inventory * node.holding_cost_per_unit

        stockout_prob = 1 - stats.norm.cdf(z)
        fill_rate = min(1.0, stats.norm.cdf(z + 0.5))  # approximate

        return PolicyResult(
            policy_name="Multi-Echelon GSM",
            node_id=node.node_id,
            sku=sku,
            reorder_point=node.demand_mean * net_lt + safety_stock,
            order_quantity=node.demand_mean,  # weekly replenishment
            safety_stock=safety_stock,
            avg_inventory=avg_inventory,
            holding_cost_weekly=holding_cost,
            service_level=target_service_level,
            fill_rate=fill_rate,
            stockout_probability=stockout_prob,
        )


# ── Trade-off Analysis: Service Level vs Cost ─────────────────
def service_cost_tradeoff(
    node: InventoryNode,
    sku: str,
    service_levels: np.ndarray = np.arange(0.80, 1.00, 0.01),
) -> pd.DataFrame:
    """Compute holding cost at various service levels for all 3 policies."""
    rq = RQHeuristic()
    bs = BaseStockPolicy()
    gsm = MultiEchelonGSM()

    rows = []
    for sl in service_levels:
        for policy, model in [("(R,Q) Heuristic", rq), ("Base-Stock", bs), ("Multi-Echelon GSM", gsm)]:
            if policy == "Multi-Echelon GSM":
                result = model.compute(node, sku, sl, parent_service_time=2)
            else:
                result = model.compute(node, sku, sl)
            rows.append({
                "service_level": round(sl * 100, 1),
                "policy": policy,
                "safety_stock": result.safety_stock,
                "avg_inventory": result.avg_inventory,
                "holding_cost_weekly": result.holding_cost_weekly,
                "fill_rate": result.fill_rate * 100,
            })

    return pd.DataFrame(rows)


# ── Build nodes from data ──────────────────────────────────────
def build_nodes_from_demand(
    demand_df: pd.DataFrame,
    network_df: pd.DataFrame,
    sku: str,
) -> Dict[str, InventoryNode]:
    """Create InventoryNode objects with computed demand stats."""
    nodes = {}
    for _, row in network_df.iterrows():
        node_id = row["node_id"]
        echelon = row["echelon"]

        # Demand stats for leaf nodes
        if echelon == 3:
            subset = demand_df[
                (demand_df["sku"] == sku) & (demand_df["warehouse"] == node_id)
            ]
            d_mean = subset["demand_units"].mean() if len(subset) > 0 else 0
            d_std = subset["demand_units"].std() if len(subset) > 0 else 0
        else:
            # Aggregate demand from children
            children = [c.strip() for c in str(row.get("children", "")).split(",") if c.strip()]
            child_demands = []
            for child in children:
                child_subset = demand_df[
                    (demand_df["sku"] == sku) & (demand_df["warehouse"] == child)
                ]
                if len(child_subset) > 0:
                    child_demands.append(child_subset["demand_units"].values)

            if child_demands:
                aggregated = sum(child_demands)
                d_mean = float(np.mean(aggregated))
                d_std = float(np.std(aggregated))
            else:
                d_mean, d_std = 0.0, 0.0

        children_list = [c.strip() for c in str(row.get("children", "")).split(",") if c.strip()]

        nodes[node_id] = InventoryNode(
            node_id=node_id,
            echelon=echelon,
            lead_time_weeks=row["lead_time_weeks"],
            holding_cost_per_unit=HOLDING_COSTS.get(echelon, 0.10),
            children=children_list,
            demand_mean=d_mean,
            demand_std=d_std,
        )

    return nodes


# ── Main ───────────────────────────────────────────────────────
if __name__ == "__main__":
    data_dir = Path(__file__).resolve().parent.parent / "data"
    demand = pd.read_csv(data_dir / "demand_history.csv", parse_dates=["date"])
    network = pd.read_csv(data_dir / "network_config.csv")

    sku = "WM-PRO-BLK"
    nodes = build_nodes_from_demand(demand, network, sku)

    print(f"\n{'═'*70}")
    print(f"  Multi-Echelon Inventory Optimisation: {sku}")
    print(f"{'═'*70}")

    # Compare all policies at each leaf node
    all_results = []
    target_sl = 0.95

    rq = RQHeuristic()
    bs = BaseStockPolicy()
    gsm = MultiEchelonGSM(committed_service_times={
        "EMEA-RDC": 1, "APAC-RDC": 1, "Americas-RDC": 1,
        "Cork-IE": 0, "Amsterdam-NL": 0, "Shanghai-CN": 0,
        "Tokyo-JP": 0, "Louisville-US": 0, "Toronto-CA": 0,
    })

    for node_id, node in nodes.items():
        if node.echelon == 3 and node.demand_mean > 0:
            r1 = rq.compute(node, sku, target_sl)
            r2 = bs.compute(node, sku, target_sl)
            r3 = gsm.compute(node, sku, target_sl, parent_service_time=2)
            all_results.extend([r1, r2, r3])

            print(f"\n  📦 {node_id} (demand μ={node.demand_mean:.0f}, σ={node.demand_std:.0f})")
            for r in [r1, r2, r3]:
                print(f"    {r.policy_name:25s}  SS={r.safety_stock:6.0f}  "
                      f"AvgInv={r.avg_inventory:7.0f}  Cost/wk=${r.holding_cost_weekly:6.1f}  "
                      f"Fill={r.fill_rate*100:5.1f}%")

    # Save results
    results_df = pd.DataFrame([r.to_dict() for r in all_results])
    results_df.to_csv(data_dir / "inventory_results.csv", index=False)
    print(f"\n✓ Inventory results saved to data/inventory_results.csv")

    # Service-cost tradeoff for one node
    cork_node = nodes.get("Cork-IE")
    if cork_node:
        tradeoff = service_cost_tradeoff(cork_node, sku)
        tradeoff.to_csv(data_dir / "tradeoff_analysis.csv", index=False)
        print(f"✓ Service-cost tradeoff saved to data/tradeoff_analysis.csv")
