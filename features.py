"""Data cleaning and feature building, shared by train.py and the app."""
import numpy as np
import pandas as pd

SERIES = ["state", "district_name", "market_name", "commodity", "variety", "grade"]
TARGET = "modal_price"
COMMODITIES = ["onion", "potato", "rice", "tomato", "wheat"]
FEATURES = [
    "r_p2", "r_p3", "r_roll5", "r_sc_prev", "r_c_prev",
    "sc_trend", "c_trend", "gap", "com", "month", "p1",
]


def clean(df):
    """Remove rows that are clearly data-entry mistakes.

    Rule 1: modal price must be inside [min_price, max_price], and max >= min.
    Rule 2: modal price must be at most 6x the median price of that commodity
            (the raw data has onion at Rs 460,000 per quintal, for example).
    """
    cap = df.groupby("commodity")[TARGET].transform("median") * 6
    bad_range = (
        (df["max_price"] < df["min_price"])
        | (df[TARGET] < df["min_price"])
        | (df[TARGET] > df["max_price"])
    )
    return df[(df[TARGET] <= cap) & ~bad_range].copy()


def _group_daily(df, keys, name):
    """Average price per day for a group, shifted so each day only sees EARLIER days."""
    d = df.groupby(keys + ["price_date"])[TARGET].mean().reset_index().sort_values("price_date")
    g = d.groupby(keys)[TARGET]
    d[name + "_prev"] = g.shift(1)
    d[name + "_prev2"] = g.shift(2)
    return d.drop(columns=TARGET)


def _ratios(df):
    """Turn raw lag prices into ratios against the last price (p1)."""
    for c in ["p2", "p3", "roll5", "sc_prev", "c_prev"]:
        df["r_" + c] = np.log(df[c] / df["p1"])
    df["sc_trend"] = np.log(df["sc_prev"] / df["sc_prev2"])
    df["c_trend"] = np.log(df["c_prev"] / df["c_prev2"])
    df["com"] = df["commodity"].map({c: i for i, c in enumerate(COMMODITIES)}).fillna(-1).astype(int)
    return df


def build_training_frame(df):
    """One row per price record, with features that use only EARLIER records.

    p1, p2, p3 : last three prices of the same market/crop/variety/grade
    roll5      : mean of its last five prices
    sc_prev    : yesterday's average for the same state + commodity
    c_prev     : yesterday's national average for the commodity
    gap        : days since the last record of this series
    Target     : log(price / p1), the change from the last price.
    """
    df = df.sort_values("price_date").reset_index(drop=True)
    g = df.groupby(SERIES, sort=False)
    for k in (1, 2, 3):
        df[f"p{k}"] = g[TARGET].shift(k)
    df["gap"] = (df["price_date"] - g["price_date"].shift(1)).dt.days
    df["roll5"] = g[TARGET].transform(lambda s: s.shift(1).rolling(5, min_periods=1).mean())
    df = df.merge(_group_daily(df, ["state", "commodity"], "sc"), on=["state", "commodity", "price_date"], how="left")
    df = df.merge(_group_daily(df, ["commodity"], "c"), on=["commodity", "price_date"], how="left")
    df["month"] = df["price_date"].dt.month
    df = df.dropna(subset=["p1", "sc_prev", "sc_prev2", "c_prev", "c_prev2"]).reset_index(drop=True)
    df = _ratios(df)
    df["y"] = np.log(df[TARGET] / df["p1"])
    return df


def build_forecast_frame(df, commodity, state):
    """Feature rows for the NEXT market day of every series in one state + commodity."""
    sub = df[(df["commodity"] == commodity) & (df["state"] == state)].sort_values("price_date")
    if sub.empty:
        return sub
    sc = sub.groupby("price_date")[TARGET].mean()
    c = df[df["commodity"] == commodity].groupby("price_date")[TARGET].mean().sort_index()
    if len(sc) < 2 or len(c) < 2:
        return sub.iloc[0:0]
    rows = []
    for key, s in sub.groupby(SERIES, sort=False):
        p = s[TARGET].to_numpy()
        rows.append({
            "market_name": key[2], "variety": key[4], "commodity": commodity,
            "last_date": s["price_date"].iloc[-1],
            "p1": p[-1],
            "p2": p[-2] if len(p) > 1 else np.nan,
            "p3": p[-3] if len(p) > 2 else np.nan,
            "roll5": p[-5:].mean(),
        })
    out = pd.DataFrame(rows)
    # Only use series that reported in the last 30 days of the data for this state.
    out = out[out["last_date"] >= sub["price_date"].max() - pd.Timedelta(days=30)].copy()
    out["sc_prev"], out["sc_prev2"] = sc.iloc[-1], sc.iloc[-2]
    out["c_prev"], out["c_prev2"] = c.iloc[-1], c.iloc[-2]
    out["gap"] = 1
    out["month"] = (sub["price_date"].max() + pd.Timedelta(days=1)).month
    return _ratios(out)
