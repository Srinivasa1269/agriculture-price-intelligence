import numpy as np
import pandas as pd
import pytest

from features import build_training_frame, clean
from query_engine import RequestError, answer, parse_question_llm, parse_question_rules, run_request, validate

STATES = ["kerala", "punjab", "tamil nadu", "uttar pradesh"]


def make_df():
    rows = []
    for d in pd.date_range("2024-01-01", periods=10):
        for state, base in [("kerala", 4000), ("punjab", 2000)]:
            for market in ["m1", "m2"]:
                rows.append(dict(state=state, district_name="d", market_name=market, commodity="onion",
                                 variety="v", grade="faq", min_price=base - 100, max_price=base + 100,
                                 modal_price=float(base), price_date=d))
    return pd.DataFrame(rows)


def test_average_is_correct():
    out = run_request(validate({"intent": "average", "commodity": "onion", "state": "kerala"}, STATES), make_df())
    assert out["ok"] and out["value"] == 4000 and out["rows"] == 20


def test_top_states_order():
    out = run_request(validate({"intent": "top_states", "commodity": "onion"}, STATES), make_df())
    assert list(out["table"]) == ["kerala", "punjab"]


def test_year_filter_no_data():
    out = run_request(validate({"intent": "average", "commodity": "onion", "year": 2020}, STATES), make_df())
    assert out["ok"] is False


def test_spelling_is_corrected():
    req = validate({"intent": "average", "commodity": "onoin", "state": "keralla"}, STATES)
    assert req["commodity"] == "onion" and req["state"] == "kerala"


@pytest.mark.parametrize("bad", [
    {"intent": "__import__('os').system('rm -rf /')", "commodity": "onion"},
    {"intent": "average", "commodity": "gold"},
    {"intent": "average", "commodity": "onion", "state": "atlantis"},
    {"intent": "average", "commodity": "onion", "year": "df.drop()"},
    "df.drop()",
])
def test_bad_requests_are_rejected(bad):
    with pytest.raises(RequestError):
        validate(bad, STATES)


@pytest.mark.parametrize("q,intent,commodity,state", [
    ("Average onion price in Punjab?", "average", "onion", "punjab"),
    ("Which state has the highest wheat price?", "top_states", "wheat", None),
    ("Predict tomato price next month in Kerala", "forecast", "tomato", "kerala"),
    ("cheapest potatoes in uttar pradesh 2024", "lowest", "potato", "uttar pradesh"),
    ("tomatoes price trend in tamil nadu", "monthly_trend", "tomato", "tamil nadu"),
])
def test_rule_parser(q, intent, commodity, state):
    req = parse_question_rules(q, STATES)
    assert (req["intent"], req["commodity"], req["state"]) == (intent, commodity, state)


class FakeLLM:
    def __init__(self, reply):
        self.reply = reply

    def invoke(self, prompt):
        return self.reply


def test_llm_json_is_parsed_not_executed():
    llm = FakeLLM('Sure! ```json\n{"intent": "average", "commodity": "onion", "state": "punjab", "year": null}\n```')
    assert parse_question_llm("x", STATES, llm)["state"] == "punjab"


def test_malicious_llm_reply_falls_back_safely():
    llm = FakeLLM("__import__('os').system('echo hacked')")
    out = answer("average onion price in kerala", make_df(), STATES, llm=llm)
    assert out["ok"] and out["value"] == 4000


def test_clean_removes_bad_rows():
    df = make_df()
    df.loc[0, "modal_price"] = 460000.0   # typing mistake
    df.loc[1, "max_price"] = 10.0         # max below min
    assert len(clean(df)) == len(df) - 2


def test_features_never_use_the_future():
    df = make_df()
    df.loc[df["price_date"] == df["price_date"].max(), "modal_price"] = 9999.0
    f = build_training_frame(df)
    before_last = f[f["price_date"] < f["price_date"].max()]
    assert (before_last[["p1", "roll5", "sc_prev", "c_prev"]] < 9999).all().all()


def test_forecast_with_stub_model():
    class Flat:
        def predict(self, X):
            return np.zeros(len(X))
    out = answer("forecast onion price in kerala", make_df(), STATES, model=Flat())
    assert out["ok"] and out["value"] == 4000 and out["markets"] == 2


def test_unknown_crop_is_not_guessed():
    out = answer("price of gold", make_df(), STATES)
    assert out["ok"] is False and "name a crop" in out["text"]
