"""
Ticker configuration for the macro weather report.

Source types:
  - "fred"        : single FRED fetch
  - "yahoo"       : single Yahoo Finance fetch
  - "yahoo_ratio" : compute ratio of two Yahoo symbols (symbol/denom * multiplier)
  - "disabled"    : skip - placeholder for unavailable data
"""

TICKERS = [
    # HEAT GAUGE (Up = Bad)
    {"name": "DXY",           "source": "yahoo", "symbol": "DX-Y.NYB",   "section": "Heat Gauge"},
    {"name": "MOVE",          "source": "yahoo", "symbol": "^MOVE",      "section": "Heat Gauge"},
    {"name": "BAMLH0A0HYM2",  "source": "fred",  "symbol": "BAMLH0A0HYM2","section": "Heat Gauge"},
    {"name": "BRENT",         "source": "yahoo", "symbol": "BZ=F",       "section": "Heat Gauge"},
    {"name": "DFII10",        "source": "fred",  "symbol": "DFII10",     "section": "Heat Gauge"},
    {"name": "VIX",           "source": "yahoo", "symbol": "^VIX",       "section": "Heat Gauge"},

    # ENGINE GAUGE (Down = Bad)
    {"name": "WALCL",         "source": "fred",  "symbol": "WALCL",      "section": "Engine Gauge"},
    {"name": "HG1!",          "source": "yahoo", "symbol": "HG=F",       "section": "Engine Gauge"},
    {"name": "GOLD",          "source": "yahoo", "symbol": "GC=F",       "section": "Engine Gauge"},
    {"name": "MCX (FTSE 250)","source": "yahoo", "symbol": "^FTMC",      "section": "Engine Gauge"},
    {"name": "LBR/GOLD*100",  "source": "yahoo_ratio", "symbol": "LBR=F", "denom": "GC=F", "multiplier": 100, "section": "Engine Gauge"},
    {"name": "CN10Y",         "source": "disabled", "section": "Engine Gauge", "note": "China 10Y - no clean free source, needs follow-up"},
    {"name": "EWY",           "source": "yahoo", "symbol": "EWY",        "section": "Engine Gauge"},

    # RECESSION CLOCK
    {"name": "T10Y2Y",        "source": "fred",  "symbol": "T10Y2Y",     "section": "Recession Clock"},
    {"name": "GB10Y-GB02Y",   "source": "disabled", "section": "Recession Clock", "note": "UK 2s10s - no clean free daily source"},

    # BENCHMARK & RISK SENTIMENT
    {"name": "US10Y",         "source": "fred",  "symbol": "DGS10",      "section": "Benchmark & Risk"},
    {"name": "GB10Y",         "source": "disabled", "section": "Benchmark & Risk", "note": "UK 10Y gilt - no clean free daily source"},
    {"name": "USDJPY",        "source": "yahoo", "symbol": "JPY=X",      "section": "Benchmark & Risk"},
    {"name": "SP500",         "source": "yahoo", "symbol": "^GSPC",      "section": "Benchmark & Risk"},

    # REAL WORLD
    {"name": "STLFSI4",       "source": "fred",  "symbol": "STLFSI4",    "section": "Real World"},
    {"name": "DRCCLT100S",    "source": "fred",  "symbol": "DRCCLT100S", "section": "Real World"},
    {"name": "WMT/TGT",       "source": "yahoo_ratio", "symbol": "WMT", "denom": "TGT", "multiplier": 1, "section": "Real World"},
    {"name": "PSAVERT",       "source": "fred",  "symbol": "PSAVERT",    "section": "Real World"},
    {"name": "UMCSENT",       "source": "fred",  "symbol": "UMCSENT",    "section": "Real World"},
    {"name": "USIJC",         "source": "fred",  "symbol": "ICSA",       "section": "Real World"},
]