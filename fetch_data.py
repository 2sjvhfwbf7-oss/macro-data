"""
Fetch 6 months of history for every ticker in tickers.py.
Returns latest value + values at 1mo/3mo/6mo ago + 6-month min/max.

Run directly to test: python3 fetch_data.py
"""

import os
import requests
import yfinance as yf
from datetime import datetime, timedelta
from dotenv import load_dotenv
from tickers import TICKERS

load_dotenv()
FRED_API_KEY = os.getenv("FRED_API_KEY")


def fetch_fred_history(series_id, days=180):
    """Get last `days` days of observations from FRED. Returns list of (date_str, value) tuples."""
    start = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
    url = "https://api.stlouisfed.org/fred/series/observations"
    params = {
        "series_id": series_id,
        "api_key": FRED_API_KEY,
        "file_type": "json",
        "observation_start": start,
        "sort_order": "asc",
    }
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    obs = response.json()["observations"]
    # FRED returns "." for missing values - skip them
    return [(o["date"], float(o["value"])) for o in obs if o["value"] != "."]


def fetch_yahoo_history(symbol, days=180, attempts=4):
    """Get last `days` days of closes from Yahoo. Returns list of (date_str, value) tuples.
    Retries with backoff: Yahoo sometimes throttles cloud runners (e.g. GitHub Actions)."""
    import time
    last_err = None
    for i in range(attempts):
        try:
            hist = yf.Ticker(symbol).history(period="6mo")
            if not hist.empty:
                return [(str(idx.date()), float(row["Close"])) for idx, row in hist.iterrows()]
            last_err = "empty response"
        except Exception as e:
            last_err = e
        time.sleep(5 * (i + 1))
    if isinstance(last_err, Exception):
        raise last_err
    return []


def fetch_yahoo_ratio_history(num_symbol, den_symbol, multiplier=1):
    """Compute ratio history from two Yahoo symbols."""
    num_hist = dict(fetch_yahoo_history(num_symbol))
    den_hist = dict(fetch_yahoo_history(den_symbol))
    # Use only dates present in both series
    common_dates = sorted(set(num_hist.keys()) & set(den_hist.keys()))
    return [
        (d, (num_hist[d] / den_hist[d]) * multiplier)
        for d in common_dates
        if den_hist[d] != 0
    ]


def summarize_history(history):
    """Given list of (date, value) sorted asc, return latest + lookbacks + min/max."""
    if not history:
        return {
            "value": None, "date": None,
            "value_1mo_ago": None, "value_3mo_ago": None, "value_6mo_ago": None,
            "min_6mo": None, "max_6mo": None,
        }

    latest_date_str, latest_value = history[-1]
    latest_dt = datetime.strptime(latest_date_str, "%Y-%m-%d")

    def closest_to(target_date):
        """Find the observation closest to target_date."""
        target_str = target_date.strftime("%Y-%m-%d")
        return min(history, key=lambda x: abs(
            (datetime.strptime(x[0], "%Y-%m-%d") - target_date).days
        ))[1]

    values = [v for _, v in history]

    return {
        "value": latest_value,
        "date": latest_date_str,
        "value_1mo_ago": closest_to(latest_dt - timedelta(days=30)),
        "value_3mo_ago": closest_to(latest_dt - timedelta(days=90)),
        "value_6mo_ago": closest_to(latest_dt - timedelta(days=180)),
        "min_6mo": min(values),
        "max_6mo": max(values),
    }


def fetch_one(t):
    """Dispatch to the right fetcher, return summary dict with error field."""
    try:
        if t["source"] == "fred":
            history = fetch_fred_history(t["symbol"])
        elif t["source"] == "yahoo":
            history = fetch_yahoo_history(t["symbol"])
        elif t["source"] == "yahoo_ratio":
            history = fetch_yahoo_ratio_history(t["symbol"], t["denom"], t.get("multiplier", 1))
        elif t["source"] == "disabled":
            return {**summarize_history([]), "error": "disabled - no data source"}
        else:
            return {**summarize_history([]), "error": "unknown source type"}

        summary = summarize_history(history)
        summary["error"] = None if summary["value"] is not None else "no data returned"
        return summary
    except Exception as e:
        return {**summarize_history([]), "error": str(e)}


def fetch_all():
    """Loop through TICKERS, fetch each, return list of results."""
    results = []
    for i, t in enumerate(TICKERS, 1):
        print(f"  [{i}/{len(TICKERS)}] Fetching {t['name']} ({t['source']})...", flush=True)
        data = fetch_one(t)
        results.append({
            "name": t["name"],
            "section": t["section"],
            "source": t["source"],
            "note": t.get("note"),
            **data,
        })
    return results


def print_summary(results):
    """Print fetched values grouped by section."""
    print(f"\n=== Fetched {len(results)} tickers at {datetime.now():%Y-%m-%d %H:%M} ===\n")
    current_section = None
    for r in results:
        if r["section"] != current_section:
            current_section = r["section"]
            print(f"\n--- {current_section} ---")
        if r["source"] == "disabled":
            print(f"  -- {r['name']:<20} DISABLED")
        elif r["error"]:
            print(f"  X  {r['name']:<20} ERROR: {r['error']}")
        else:
            print(
                f"  OK {r['name']:<20} "
                f"now: {r['value']:>10,.2f}  "
                f"1mo: {r['value_1mo_ago']:>10,.2f}  "
                f"3mo: {r['value_3mo_ago']:>10,.2f}  "
                f"6mo: {r['value_6mo_ago']:>10,.2f}  "
                f"range: {r['min_6mo']:,.2f}-{r['max_6mo']:,.2f}"
            )
    ok = sum(1 for r in results if not r["error"] and r["source"] != "disabled")
    disabled = sum(1 for r in results if r["source"] == "disabled")
    errors = sum(1 for r in results if r["error"] and r["source"] != "disabled")
    print(f"\n{ok} ok, {disabled} disabled, {errors} errors (total {len(results)})")


if __name__ == "__main__":
    results = fetch_all()
    print_summary(results)