# Agriculture Price Intelligence

Ask questions about Indian crop (mandi) prices in plain English, and get a short-term price forecast.

- **Data:** 737,392 daily market price records (June 2023 to June 2025) for onion, potato, rice, tomato and wheat across 26 states.
- **Model:** XGBoost forecast of the next market-day price, tested on data from a later year.
- **App:** Streamlit. A local Mistral model (Ollama + LangChain) turns the question into a small JSON request. The code then runs only fixed, safe Pandas operations.

> This is a **text-to-query assistant plus a forecasting model**. It is **not** a RAG system: there is no vector database or document retrieval.

## Results (honest numbers)

Task: predict the next modal price (Rs per quintal) of a market / crop / variety / grade.
Test: **time split** - train on 2023-2024 (564,426 rows), test on 2025 (162,691 rows).

| Model | R² | RMSE (Rs) | MAE (Rs) |
|---|---|---|---|
| Naive baseline (repeat the last price) | 0.955 | 270.8 | 100.7 |
| Linear Regression | 0.953 | 276.3 | 130.1 |
| **XGBoost** | **0.967** | **233.3** | 101.6 |

What this means:

- XGBoost has **14% lower RMSE** than the naive baseline. It is better at the big price moves.
- MAE is about the **same** as the baseline. On a normal day prices barely change, so "repeat the last price" is very hard to beat.
- The high R² mostly comes from the last price. The fair comparison is always **model vs baseline**, not R² alone.

Full numbers, including per-crop scores, are in `models/metrics.json` (written by `train.py`).

### How the model got here

1. First version (see `notebooks/agriculture_eda.ipynb`): only state, commodity and month as inputs. Best R² was **0.48** on a random split.
2. Adding market, district and variety gave R² 0.70-0.78 on a random split, but a **negative** R² on a time split. The model had memorised price levels and could not handle a new year.
3. Final version: predict the **change from the last price** using lag features (last 3 prices, 5-record average, yesterday's state and national averages). This is the version in the table.

## Honest design choices

- `min_price` and `max_price` of the same day are **not** model inputs. They are nearly the same number as the target (leakage).
- Every feature uses only **earlier** records. A unit test checks this.
- 2,393 rows are removed as data-entry mistakes: modal price outside the min-max range, or more than 6x the crop's median price (the raw data has onion at Rs 460,000 per quintal).

## Safe question answering

The first version asked the LLM to write Pandas code and ran it with `eval()`. That is unsafe, because the model could write any Python.

Now (`query_engine.py`):

1. The LLM returns only JSON, for example `{"intent": "average", "commodity": "onion", "state": "rajasthan", "year": null}`.
2. The JSON is validated against fixed lists of intents, crops and states.
3. One of seven fixed Pandas operations runs: `average`, `highest`, `lowest`, `top_states`, `bottom_states`, `monthly_trend`, `forecast`.
4. If Ollama is not running, a keyword parser does step 1, so the app still works.

No generated code is ever executed.

## Run it

```bash
pip install -r requirements.txt
# put agriculture_cleaned.csv in data/  (see "Data" below)
python train.py            # about 1 minute, writes models/
python -m pytest tests     # 20 tests
streamlit run app.py
```

Optional, for the LLM: install [Ollama](https://ollama.com) and run `ollama pull mistral`.

## Files

| File | What it does |
|---|---|
| `features.py` | Data cleaning and lag features (shared by training and the app) |
| `train.py` | Trains the models, compares with the baseline, saves metrics |
| `query_engine.py` | Question -> JSON request -> whitelisted Pandas operation |
| `app.py`, `ui_style.py` | Streamlit app and its styling |
| `tests/` | Unit tests for the query engine, cleaning and features |
| `notebooks/agriculture_eda.ipynb` | First exploration and first model comparison |

## Data

The CSV files (55-62 MB) are not in this repository. The data is daily mandi (market) price data from India with the columns: state, district, market, commodity, variety, grade, min/max/modal price and date.

**Source:** TODO - add the link to the dataset page you downloaded it from.

## Limits

- The forecast is for the **next market day only**, not weeks ahead.
- Crop coverage is uneven: tomato has data only in 2023, wheat ends in early 2024, and rice appears only in 2025. The 2025 test set therefore covers onion, potato and rice.
- The forecast for a state is the average over its market series that reported in the last 30 days of the data.
- The LLM part needs Ollama on the same machine, so the app cannot be hosted for free as is. The keyword parser works without it.
- The Ollama path was not run in automated tests. The tests use a fake LLM to check JSON parsing and the safe fallback.
