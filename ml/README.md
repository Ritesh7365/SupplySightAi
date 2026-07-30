# Machine Learning — SupplySight AI

## Purpose

Offline and online ML assets for delay prediction, demand forecasting, inventory prediction, and vendor risk — including feature engineering, training entrypoints, model registry folders, artifacts, and evaluation reports.

## Contents

| Path | Role |
|------|------|
| `delay_prediction/` | Delivery delay models |
| `demand_forecasting/` | Demand / SKU forecast models |
| `inventory_prediction/` | Inventory / reorder models |
| `vendor_risk/` | Vendor risk scoring |
| `feature_engineering/` | Shared feature builders |
| `training/` | Training orchestration scripts |
| `models/` | Serialized model store (binaries gitignored) |
| `artifacts/` | Metrics, plots, metadata |
| `evaluation/` | Evaluation notebooks/scripts and reports |

## Stack (planned)

Pandas, NumPy, Scikit-Learn, XGBoost, LightGBM, Prophet, SHAP

## Future Implementation

- Reproducible training configs and experiment tracking
- Model cards and promotion criteria
- Inference contracts consumed by `backend/app/ml`

> No model training in this initialization phase.
