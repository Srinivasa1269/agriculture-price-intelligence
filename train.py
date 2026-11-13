"""Train the crop price model and report honest scores.

Run:  python train.py
Writes: models/xgb_model.json and models/metrics.json

Task: predict the next modal price (Rs per quintal) of a market/crop/variety/grade
from its own recent prices and yesterday's state and national averages.

Honest choices:
1. min_price and max_price of the same day are NOT inputs (that would be leakage).
2. The test set is a TIME split: train on 2023-2024, test on 2025. A random split
   is too easy because neighbouring days are nearly identical.
3. Every score is compared with a naive baseline: "tomorrow = last known price".
   A model is only useful if it beats that baseline.
"""
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from xgboost import XGBRegressor

from features import FEATURES, TARGET, build_training_frame, clean

DATA = Path("data/agriculture_cleaned.csv")
OUT = Path("models")
SPLIT_DATE = "2025-01-01"


def metrics(y_true, pred):
    return {
        "r2": round(float(r2_score(y_true, pred)), 4),
        "rmse": round(float(np.sqrt(mean_squared_error(y_true, pred))), 1),
        "mae": round(float(mean_absolute_error(y_true, pred)), 1),
    }


def make_xgb():
    return XGBRegressor(
        objective="reg:pseudohubererror", huber_slope=0.05,
        n_estimators=300, max_depth=6, learning_rate=0.05,
        subsample=0.8, colsample_bytree=0.8, min_child_weight=20,
        n_jobs=-1, random_state=42,
    )


def main():
    raw = pd.read_csv(DATA, parse_dates=["price_date"])
    cleaned = clean(raw)
    df = build_training_frame(cleaned)
    print(f"rows: raw {len(raw)}, after cleaning {len(cleaned)}, with features {len(df)}")

    X = df[FEATURES].fillna(0.0)
    tr = df["price_date"] < SPLIT_DATE
    te = df[~tr]

    results = {
        "rows_raw": int(len(raw)), "rows_after_cleaning": int(len(cleaned)),
        "train_rows": int(tr.sum()), "test_rows": int(len(te)),
        "split": f"train before {SPLIT_DATE}, test from {SPLIT_DATE}",
        "scores": {},
    }
    preds = {"Naive baseline (last price)": te["p1"]}
    for name, model in {"Linear Regression": LinearRegression(), "XGBoost": make_xgb()}.items():
        model.fit(X[tr], df.loc[tr, "y"])
        preds[name] = te["p1"] * np.exp(model.predict(X[~tr]))
    for name, p in preds.items():
        results["scores"][name] = metrics(te[TARGET], p)
        print(f"  {name:<30} {results['scores'][name]}")

    results["by_commodity"] = {}
    for com in sorted(te["commodity"].unique()):
        k = te["commodity"] == com
        results["by_commodity"][com] = {
            "test_rows": int(k.sum()),
            "baseline": metrics(te[TARGET][k], preds["Naive baseline (last price)"][k]),
            "xgboost": metrics(te[TARGET][k], preds["XGBoost"][k]),
        }

    final = make_xgb()
    final.fit(X, df["y"])  # final model uses all data
    OUT.mkdir(exist_ok=True)
    final.save_model(OUT / "xgb_model.json")
    (OUT / "metrics.json").write_text(json.dumps(results, indent=2))
    print("saved models/xgb_model.json and models/metrics.json")


if __name__ == "__main__":
    main()
