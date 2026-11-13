"""Safe question answering over the price data.

The old version asked the LLM to write Pandas code and ran it with eval().
That is unsafe: the model could write any Python. Now the LLM (or a simple
keyword parser) only fills in a small request like

    {"intent": "average", "commodity": "onion", "state": "rajasthan", "year": null}

and this file runs one of a fixed list of Pandas operations. No generated code
is ever executed.
"""
import json
import re
from difflib import get_close_matches

import numpy as np
import pandas as pd

from features import COMMODITIES, FEATURES, TARGET, build_forecast_frame

INTENTS = ["average", "highest", "lowest", "top_states", "bottom_states", "monthly_trend", "forecast"]


class RequestError(ValueError):
    """The question could not be turned into a valid request."""


def _match(word, options):
    if not word:
        return None
    m = get_close_matches(str(word).lower().strip(), options, n=1, cutoff=0.75)
    return m[0] if m else None


def validate(req, states):
    """Check a request dict and return a clean copy. Raises RequestError if invalid."""
    if not isinstance(req, dict):
        raise RequestError("Request must be a JSON object.")
    intent = req.get("intent")
    if intent not in INTENTS:
        raise RequestError(f"Unknown intent: {intent!r}")
    commodity = _match(req.get("commodity"), COMMODITIES)
    if commodity is None:
        raise RequestError("Please name a crop: " + ", ".join(COMMODITIES) + ".")
    state = _match(req.get("state"), states)
    if req.get("state") and state is None:
        raise RequestError(f"Unknown state: {req.get('state')!r}")
    if intent == "forecast" and state is None:
        raise RequestError("Please name a state for a forecast.")
    year = req.get("year")
    try:
        year = int(year) if year not in (None, "") else None
    except (TypeError, ValueError):
        raise RequestError(f"Bad year: {year!r}")
    return {"intent": intent, "commodity": commodity, "state": state, "year": year}


def parse_question_rules(question, states):
    """Keyword parser. Works with no LLM at all (used as fallback and in tests)."""
    q = question.lower()
    words = re.findall(r"[a-z&]+", q)
    commodity = None
    for w in words:
        if w in ("price", "prices", "priced"):  # "price" looks like "rice" to a fuzzy matcher
            continue
        commodity = _match(w, COMMODITIES) or _match(w.rstrip("s"), COMMODITIES) or _match(w[:-2], COMMODITIES)
        if commodity:
            break
    state = next((s for s in sorted(states, key=len, reverse=True) if s in q), None)
    if state is None:
        state = next((s for w in words if len(w) > 3 and (s := _match(w, states))), None)
    year = next((int(y) for y in re.findall(r"\b(20\d\d)\b", q)), None)
    if any(k in q for k in ["predict", "forecast", "next", "tomorrow", "will be", "expected", "upcoming"]):
        intent = "forecast"
    elif any(k in q for k in ["trend", "monthly", "over time", "by month"]):
        intent = "monthly_trend"
    elif any(k in q for k in ["which state", "what state", "states"]) and any(k in q for k in ["cheapest", "lowest", "least"]):
        intent = "bottom_states"
    elif any(k in q for k in ["which state", "what state", "states"]):
        intent = "top_states"
    elif any(k in q for k in ["highest", "maximum", "max ", "most expensive"]):
        intent = "top_states" if state is None else "highest"
    elif any(k in q for k in ["lowest", "minimum", "min ", "cheapest"]):
        intent = "bottom_states" if state is None else "lowest"
    else:
        intent = "average"
    return {"intent": intent, "commodity": commodity, "state": state, "year": year}


LLM_PROMPT = """Turn the question into JSON. Reply with JSON only.
Keys: "intent", "commodity", "state", "year".
intent is one of: {intents}
  average = average price; highest / lowest = highest or lowest price in one state;
  top_states / bottom_states = which states are most / least expensive;
  monthly_trend = price by month; forecast = predict the next price.
commodity is one of: {commodities}
state is one of: {states}  (or null)
year is a number like 2024, or null.

Question: {question}
JSON:"""


def parse_question_llm(question, states, llm):
    """Ask the LLM for the JSON request. The reply is parsed as data, never executed."""
    text = llm.invoke(LLM_PROMPT.format(
        intents=", ".join(INTENTS), commodities=", ".join(COMMODITIES),
        states=", ".join(states), question=question,
    ))
    m = re.search(r"\{.*\}", str(text), re.S)
    if not m:
        raise RequestError("The model did not return JSON.")
    try:
        return json.loads(m.group(0))
    except json.JSONDecodeError as e:
        raise RequestError(f"Bad JSON from the model: {e}")


def run_request(req, df, model=None):
    """Run one whitelisted operation. Returns a dict with the numbers and a plain sentence."""
    c, s, y, intent = req["commodity"], req["state"], req["year"], req["intent"]
    if intent == "forecast":
        return _forecast(df, model, c, s)
    sub = df[df["commodity"] == c]
    if s:
        sub = sub[sub["state"] == s]
    if y:
        sub = sub[sub["price_date"].dt.year == y]
    if sub.empty:
        return {"ok": False, "text": "No data found for this question."}
    where = f" in {s.title()}" if s else " across India"
    when = f" in {y}" if y else ""
    if intent in ("average", "highest", "lowest"):
        fn = {"average": "mean", "highest": "max", "lowest": "min"}[intent]
        value = float(getattr(sub[TARGET], fn)())
        return {"ok": True, "value": round(value, 2), "rows": int(len(sub)),
                "text": f"The {intent} {c} price{where}{when} is Rs {value:,.0f} per quintal ({len(sub):,} records)."}
    if intent in ("top_states", "bottom_states"):
        by = sub.groupby("state")[TARGET].mean().sort_values(ascending=(intent == "bottom_states")).head(5).round(0)
        word = "highest" if intent == "top_states" else "lowest"
        listing = ", ".join(f"{k.title()} (Rs {v:,.0f})" for k, v in by.items())
        return {"ok": True, "table": by.to_dict(), "text": f"States with the {word} average {c} price{when}: {listing}."}
    if intent == "monthly_trend":
        by = sub.groupby(sub["price_date"].dt.to_period("M"))[TARGET].mean().round(0)
        first, last = by.iloc[0], by.iloc[-1]
        return {"ok": True, "table": {str(k): v for k, v in by.items()},
                "text": f"Average {c} price{where}{when} went from Rs {first:,.0f} ({by.index[0]}) to Rs {last:,.0f} ({by.index[-1]})."}
    raise RequestError(f"Unknown intent: {intent!r}")


def _forecast(df, model, commodity, state):
    if model is None:
        return {"ok": False, "text": "The forecast model is not loaded. Run train.py first."}
    rows = build_forecast_frame(df, commodity, state)
    if rows.empty:
        return {"ok": False, "text": f"Not enough recent {commodity} data in {state.title()} to forecast."}
    pred = rows["p1"] * np.exp(model.predict(rows[FEATURES].fillna(0.0)))
    last, nxt = float(rows["p1"].mean()), float(pred.mean())
    change = (nxt / last - 1) * 100
    return {"ok": True, "value": round(nxt, 2), "last": round(last, 2), "markets": int(len(rows)),
            "last_date": str(rows["last_date"].max().date()),
            "text": (f"Forecast for the next market day after {rows['last_date'].max().date()}: {commodity} in "
                     f"{state.title()} about Rs {nxt:,.0f} per quintal, {change:+.1f}% vs the last price of "
                     f"Rs {last:,.0f} (average over {len(rows)} market series).")}


def answer(question, df, states, model=None, llm=None):
    """Full pipeline: question -> request -> whitelisted operation -> sentence."""
    req = None
    if llm is not None:
        try:
            req = validate(parse_question_llm(question, states, llm), states)
        except Exception:
            req = None  # fall back to the keyword parser
    if req is None:
        try:
            req = validate(parse_question_rules(question, states), states)
        except RequestError as e:
            return {"ok": False, "text": str(e)}
    out = run_request(req, df, model)
    out["request"] = req
    return out
