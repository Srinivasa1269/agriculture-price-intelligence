"""Agriculture Price Intelligence - Streamlit app.

Run:  streamlit run app.py

Ask a question in plain English. The question becomes a small JSON request
(by a local Mistral model through Ollama, or by a keyword parser if Ollama is
not running). Only fixed, whitelisted Pandas operations are run - see
query_engine.py. Forecasts come from the XGBoost model trained in train.py.
"""
import json
from pathlib import Path

import pandas as pd
import streamlit as st
from xgboost import XGBRegressor

from features import clean
from query_engine import answer
from ui_style import CSS

st.set_page_config(page_title="Agriculture Price Intelligence", page_icon="🌾", layout="centered")
st.markdown(CSS, unsafe_allow_html=True)


@st.cache_resource
def load_data():
    df = pd.read_csv("data/agriculture_cleaned.csv", parse_dates=["price_date"])
    return clean(df)


@st.cache_resource
def load_model():
    path = Path("models/xgb_model.json")
    if not path.exists():
        return None
    model = XGBRegressor()
    model.load_model(path)
    return model


@st.cache_resource
def load_llm():
    """Local Mistral through Ollama. Returns None if Ollama is not available."""
    try:
        from langchain_ollama import OllamaLLM
        llm = OllamaLLM(model="mistral")
        llm.invoke("Reply with the word ok.")
        return llm
    except Exception:
        return None


df = load_data()
model = load_model()
llm = load_llm()
states = sorted(df["state"].unique())


def explain(question, result):
    """Let the LLM rewrite the answer in friendly words. Numbers come from our code."""
    if llm is None or not result.get("ok"):
        return result["text"]
    prompt = (f"User asked: {question}\nFacts: {result['text']}\n"
              "Rewrite the facts in 2 short simple sentences. Keep every number exactly the same. "
              "Do not add new numbers.")
    try:
        return str(llm.invoke(prompt)).strip()
    except Exception:
        return result["text"]


st.markdown("<h1>🌾 Agriculture Price Intelligence</h1>", unsafe_allow_html=True)
st.markdown("<p>Ask any question about crop prices across India</p>", unsafe_allow_html=True)
st.markdown("<hr>", unsafe_allow_html=True)
st.markdown("""
<p class='try-label'>Try asking</p>
<div style='text-align:center; margin-bottom:1.6rem;'>
  <span class='example-tag'>Average onion price in Rajasthan?</span>
  <span class='example-tag'>Which state has the highest wheat price?</span>
  <span class='example-tag'>Forecast potato price in Punjab</span>
</div>
""", unsafe_allow_html=True)

with st.form("ask"):
    question = st.text_input("Your question", placeholder="e.g. What is the average potato price in Punjab?",
                             label_visibility="collapsed")
    asked = st.form_submit_button("🌿 Ask", use_container_width=True)

if asked:
    if not question.strip():
        st.warning("Please type a question first.")
    else:
        with st.spinner("🌱 Finding answer..."):
            result = answer(question.strip(), df, states, model=model, llm=llm)
            text = explain(question, result)
        st.markdown(f"<div class='answer-box'>{text}</div>", unsafe_allow_html=True)
        if result.get("table"):
            st.bar_chart(pd.Series(result["table"], name="Average price (Rs/quintal)"))
        if result.get("request", {}).get("intent") == "forecast" and result.get("ok"):
            m = json.loads(Path("models/metrics.json").read_text())["scores"]
            st.caption(f"Model test (2025 data): RMSE Rs {m['XGBoost']['rmse']} vs Rs "
                       f"{m['Naive baseline (last price)']['rmse']} for the naive last-price baseline.")

st.caption("Language model: " + ("Mistral via Ollama" if llm else "not running - using the keyword parser"))
