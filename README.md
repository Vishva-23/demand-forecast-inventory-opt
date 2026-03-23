# Probabilistic Demand Forecasting & Multi-Echelon Inventory Optimisation

A Python-based decision support tool for supply chain planning that combines **probabilistic demand forecasting** with **multi-echelon inventory optimisation**, comparing heuristic vs. optimisation-based policies across a three-tier distribution network.

> **Context:** Built as part of MSc Data Science & Analytics coursework at University College Cork, applying modules in Statistical Modelling (ST6030), Machine Learning (ST6041), and Optimisation (CS6322) to a realistic consumer electronics supply chain scenario.

---

## Problem Statement

Global supply chains must balance **service levels** (avoiding stockouts) against **holding costs** (excess inventory). This project addresses two linked challenges:

1. **Demand Uncertainty** — How do we generate reliable probabilistic forecasts (not just point estimates) across product/location hierarchies?
2. **Inventory Policy Selection** — Given uncertain demand, which inventory policy minimises cost while meeting service-level targets across a multi-echelon network?

## Architecture

```
Product Hierarchy              Network Hierarchy (3 Echelons)
─────────────────              ──────────────────────────────
Product Family                     Central DC (Global HQ)
  └── SKU                         ┌────┼────┐
       └── Region                EMEA  APAC  Americas   ← Regional DCs
            └── Warehouse        │  │  │  │   │    │
                                 IE NL CN JP  US   CA   ← Local Warehouses
```

**11 SKUs × 6 Warehouses × 104 Weeks** = 6,864 demand observations with realistic seasonality, trend, and noise.

## Forecasting Models

| Model | Approach | Uncertainty Method |
|-------|----------|-------------------|
| **Holt-Winters** | Triple exponential smoothing (multiplicative seasonality) | Residual-based prediction intervals |
| **Bayesian STS** | Structural time series decomposition | Monte Carlo sampling (200 draws) |
| **Quantile Regression** | Feature-engineered gradient boosting | Direct quantile estimation (P10/P50/P90) |

Each model produces **P10, P50, P90** prediction intervals — critical for safety stock calculations.

## Inventory Policies

| Policy | Type | Best For |
|--------|------|----------|
| **(R,Q) Heuristic** | Reorder-point / EOQ | Simple single-echelon setups |
| **Base-Stock (S)** | Order-up-to level | Periodic review systems |
| **Multi-Echelon GSM** | Guaranteed-service model | Networks with committed service times |

### Key Trade-off: Service Level vs. Holding Cost

The tool generates Pareto frontiers showing how each policy performs across service levels (80–99%), enabling planners to select the optimal operating point.

## Quick Start

```bash
# Clone and install
git clone https://github.com/Vishva-23/demand-forecast-inventory-opt.git
cd demand-forecast-inventory-opt
pip install -r requirements.txt

# Generate sample data
python src/generate_data.py

# Run forecasting models
python src/forecast.py

# Run inventory optimisation
python src/inventory_opt.py
```

## Project Structure

```
demand-forecast-inventory-opt/
├── data/
│   ├── demand_history.csv        # Generated demand data (6,864 rows)
│   ├── network_config.csv        # 3-echelon network topology
│   ├── forecast_results.csv      # Model outputs with prediction intervals
│   ├── inventory_results.csv     # Policy comparison across warehouses
│   └── tradeoff_analysis.csv     # Service level vs. cost curves
├── src/
│   ├── generate_data.py          # Realistic data generator
│   ├── forecast.py               # 3 forecasting models + evaluation
│   └── inventory_opt.py          # 3 inventory policies + trade-off analysis
├── docs/
│   └── methodology.md            # Detailed methodology notes
├── dashboard.html                # Interactive browser-based dashboard
├── requirements.txt
└── README.md
```

## Results Summary (WM-PRO-BLK @ Cork-IE)

### Forecast Accuracy
| Model | MAPE | RMSE | P10–P90 Coverage |
|-------|------|------|-----------------|
| Holt-Winters | 19.2% | 10.9 | 87.5% |
| Bayesian STS | 19.8% | 11.6 | 81.2% |
| Quantile Regression | 44.2% | 21.9 | 100.0% |

**Insight:** Holt-Winters provides the best point accuracy, while Bayesian STS achieves near-optimal coverage with tighter intervals — making it the best choice for safety stock inputs.

### Inventory Policy Comparison (95% Service Level)
| Policy | Safety Stock | Avg Inventory | Weekly Cost |
|--------|-------------|---------------|-------------|
| (R,Q) Heuristic | 22 | 626 | $125.19 |
| Base-Stock | 31 | 59 | $11.73 |
| Multi-Echelon GSM | 37 | 66 | $13.10 |

**Insight:** The Base-Stock policy achieves **90.6% lower holding cost** than the naive (R,Q) heuristic at the same service level. The Multi-Echelon GSM adds only $1.37/week while accounting for network-level service guarantees.

## Relevance to Supply Chain Planning

This framework directly supports:
- **Strategic deal demand planning** — Probabilistic forecasts feed safety stock calculations for promotional/deal volumes
- **Continuous improvement** — Trade-off analysis enables data-driven policy recommendations
- **S&OP/IBP alignment** — Scenario comparison (base/upside/downside) across the network hierarchy

## Tech Stack

- **Python** (Pandas, NumPy, SciPy, Matplotlib)
- **Statistical Methods** — Exponential smoothing, Bayesian structural decomposition, quantile regression
- **Optimisation** — Service-level constrained inventory optimisation, EOQ, guaranteed-service models

## License

MIT

## Author

**Vishvasundar S** — MSc Data Science & Analytics, University College Cork
