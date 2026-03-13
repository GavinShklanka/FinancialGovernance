"""
Antigravity — Market data fetcher (Stage 1) — Live API + Fallback.

Strategy: try live API calls when keys are present in .env.
          Gracefully fall back to representative sample data if any key
          is missing or an API call fails.

Live data sources:
  - Alpha Vantage  → SPY price (ALPHAVANTAGE_API_KEY)
  - FRED           → 10Y yield, VIX proxy  (FRED_API_KEY)
  - Nasdaq Data Link → uranium spot        (NASDAQ_DATA_LINK_API_KEY)
  - NewsAPI        → cyber incident count  (NEWS_API_KEY)

Minimum keys to start: FRED_API_KEY + ALPHAVANTAGE_API_KEY
Everything else falls back gracefully.
"""

import json
import os
from datetime import datetime, timezone
from app.data.cache_engine import cached_fetch
from system_integrity.atomic_writer import atomic_write_json
from system_integrity.snapshot_validator import validate_json_structure
from system_integrity.recovery_manager import backup_snapshot

# Load .env before any key reads
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass  # dotenv not installed — keys must be set in environment manually


SNAPSHOT_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "data", "raw"
)
SNAPSHOT_PATH = os.path.join(SNAPSHOT_DIR, "market_snapshot.json")


# ── Sample data (used when API key absent or call fails) ─────────────────────

_SAMPLE_SNAPSHOT = {
    "spy_price":                 512.34,
    "vix":                       18.7,
    "dxy":                       104.25,
    "tnx_yield":                 4.32,
    "gold_price":                2185.50,
    "btc_price":                 71250.00,
    "copper_inventories":        185.0,
    "uranium_spot":              95.50,
    "semi_equipment_orders":     18.5,
    "hyperscaler_capex_signal":  8.2,
    "cyber_incidents":           62.0,
    "china_pmi":                 50.8,
    "electricity_demand_signal": 4.1,
    "equities": {
        "NVDA": {"price": 850.0},
        "AMD": {"price": 180.0},
        "TSM": {"price": 140.0},
        "ASML": {"price": 950.0},
        "MSFT": {"price": 420.0},
        "AMZN": {"price": 175.0},
        "GOOGL": {"price": 145.0},
        "META": {"price": 500.0}
    },
    "macro": {
        "SPY": {"price": 512.34},
        "VIX": {"value": 18.7},
        "DXY": {"value": 104.25},
        "Gold": {"price": 2185.50}
    },
    "crypto": {
        "BTC": {"price": 71250.00}
    }
}


# ── Live fetch helpers ────────────────────────────────────────────────────────

def _fetch_alphavantage_price(symbol: str, key: str) -> float | None:
    """Fetch latest closing price from Alpha Vantage."""
    try:
        import requests
        url = (
            f"https://www.alphavantage.co/query"
            f"?function=GLOBAL_QUOTE&symbol={symbol}&apikey={key}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        price_str = data.get("Global Quote", {}).get("05. price")
        return float(price_str) if price_str else None
    except Exception as e:
        print(f"    [WARN] Alpha Vantage fetch failed for {symbol}: {e}")
        return None


def _fetch_fred_series(series_id: str, key: str) -> float | None:
    """Fetch latest value from a FRED data series."""
    try:
        import requests
        url = (
            f"https://api.stlouisfed.org/fred/series/observations"
            f"?series_id={series_id}&api_key={key}&file_type=json"
            f"&sort_order=desc&limit=1"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        obs = r.json().get("observations", [])
        if obs:
            val = obs[0].get("value", ".")
            return float(val) if val != "." else None
    except Exception as e:
        print(f"    [WARN] FRED fetch failed for {series_id}: {e}")
    return None


def _fetch_newsapi_cyber_count(key: str) -> float | None:
    """Estimate weekly cyber incident count from NewsAPI headlines."""
    try:
        import requests
        url = (
            "https://newsapi.org/v2/everything"
            "?q=cybersecurity+breach+attack+ransomware"
            "&language=en&pageSize=100&sortBy=publishedAt"
            f"&apiKey={key}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        count = r.json().get("totalResults", 0)
        # Scale to weekly incident proxy: cap at 200, normalize to 0–100
        return min(float(count), 200.0)
    except Exception as e:
        print(f"    [WARN] NewsAPI fetch failed: {e}")
    return None


def _fetch_nasdaq_uranium(key: str) -> float | None:
    """Fetch uranium spot price from Nasdaq Data Link (UX1 futures proxy)."""
    try:
        import requests
        url = (
            f"https://data.nasdaq.com/api/v3/datasets/CHRIS/CME_UX1.json"
            f"?api_key={key}&rows=1"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        data = r.json().get("dataset", {})
        rows = data.get("data", [])
        if rows:
            # Column 4 = Settle price
            return float(rows[0][4])
    except Exception as e:
        print(f"    [WARN] Nasdaq Data Link uranium fetch failed: {e}")
    return None


# ── Main fetch function ───────────────────────────────────────────────────────

def fetch_and_store_market_snapshot() -> None:
    """
    Attempt live API fetches for each data point.
    If a key is missing or call fails, use sample value.
    """
    print("  [Stage 1] Fetching market data...")

    av_key   = os.getenv("ALPHAVANTAGE_API_KEY")
    fred_key = os.getenv("FRED_API_KEY")
    news_key = os.getenv("NEWS_API_KEY")
    ndl_key  = os.getenv("NASDAQ_DATA_LINK_API_KEY")

    snapshot: dict = dict(_SAMPLE_SNAPSHOT)  # start with sample defaults
    snapshot["timestamp"] = datetime.now(timezone.utc).isoformat()

    # ── SPY price ──
    if av_key:
        val = cached_fetch(
            "alphavantage_spy", 
            lambda: _fetch_alphavantage_price("SPY", av_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["spy_price"] = val
            snapshot.setdefault("macro", {})["SPY"] = {"price": val}
            print(f"    ✓ SPY: ${val:,.2f} (live/cached)")
        else:
            print(f"    ~ SPY: ${snapshot['spy_price']:,.2f} (sample fallback)")
    else:
        print(f"    ~ SPY: ${snapshot['spy_price']:,.2f} (no ALPHAVANTAGE_API_KEY)")

    # ── AI Equities ──
    ai_tickers = ["NVDA", "AMD", "TSM", "ASML", "MSFT", "AMZN", "GOOGL", "META"]
    snapshot.setdefault("equities", {})
    for ticker in ai_tickers:
        if av_key:
            val = cached_fetch(
                f"alphavantage_{ticker.lower()}",
                lambda t=ticker: _fetch_alphavantage_price(t, av_key),
                ttl_seconds=3600
            )
            if val is not None:
                snapshot["equities"][ticker] = {"price": val}
                print(f"    ✓ {ticker}: ${val:,.2f} (live/cached)")
            else:
                price = _SAMPLE_SNAPSHOT["equities"][ticker]["price"]
                snapshot["equities"][ticker] = {"price": price}
                print(f"    ~ {ticker}: ${price:,.2f} (sample fallback)")
        else:
            price = _SAMPLE_SNAPSHOT["equities"][ticker]["price"]
            snapshot["equities"][ticker] = {"price": price}

    # ── Gold price ──
    if av_key:
        val = cached_fetch(
            "alphavantage_gld",
            lambda: _fetch_alphavantage_price("GLD", av_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["gold_price"] = val * 9.3  # GLD ≈ 1/10 oz; scale to spot approx
            snapshot.setdefault("macro", {})["Gold"] = {"price": snapshot["gold_price"]}
            print(f"    ✓ Gold: ${snapshot['gold_price']:,.2f} (live/cached GLD proxy)")

    # ── 10Y Yield — FRED series DGS10 ──
    if fred_key:
        val = cached_fetch(
            "fred_dgs10",
            lambda: _fetch_fred_series("DGS10", fred_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["tnx_yield"] = val
            print(f"    ✓ 10Y Yield: {val}% (live/cached FRED)")
        else:
            print(f"    ~ 10Y Yield: {snapshot['tnx_yield']}% (sample fallback)")
    else:
        print(f"    ~ 10Y Yield: {snapshot['tnx_yield']}% (no FRED_API_KEY)")

    # ── VIX — FRED series VIXCLS ──
    if fred_key:
        val = cached_fetch(
            "fred_vixcls",
            lambda: _fetch_fred_series("VIXCLS", fred_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["vix"] = val
            print(f"    ✓ VIX: {val} (live/cached FRED)")

    # ── DXY — FRED series DTWEXBGS ──
    if fred_key:
        val = cached_fetch(
            "fred_dtwexbgs",
            lambda: _fetch_fred_series("DTWEXBGS", fred_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["dxy"] = val
            print(f"    ✓ DXY: {val} (live/cached FRED)")

    # ── China PMI — FRED (CHNMFPMI) ──
    if fred_key:
        val = cached_fetch(
            "fred_chnmfpmi",
            lambda: _fetch_fred_series("CHNMFPMI", fred_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["china_pmi"] = val
            print(f"    ✓ China PMI: {val} (live/cached FRED)")

    # ── Uranium spot — Nasdaq Data Link ──
    if ndl_key:
        val = cached_fetch(
            "nasdaq_uranium",
            lambda: _fetch_nasdaq_uranium(ndl_key),
            ttl_seconds=3600
        )
        if val:
            snapshot["uranium_spot"] = val
            print(f"    ✓ Uranium spot: ${val}/lb (live/cached Nasdaq DL)")
        else:
            print(f"    ~ Uranium: ${snapshot['uranium_spot']}/lb (sample fallback)")
    else:
        print(f"    ~ Uranium: ${snapshot['uranium_spot']}/lb (no NASDAQ_DATA_LINK_API_KEY)")

    # ── Cyber incidents — NewsAPI ──
    if news_key:
        val = cached_fetch(
            "newsapi_cyber",
            lambda: _fetch_newsapi_cyber_count(news_key),
            ttl_seconds=3600
        )
        if val is not None:
            snapshot["cyber_incidents"] = val
            print(f"    ✓ Cyber incidents: {val:.0f}/week (live/cached NewsAPI)")
        else:
            print(f"    ~ Cyber incidents: {snapshot['cyber_incidents']:.0f} (sample fallback)")
    else:
        print(f"    ~ Cyber incidents: {snapshot['cyber_incidents']:.0f} (no NEWS_API_KEY)")

    # ── Remaining signals use sample data (no public free API tier) ──
    # copper_inventories, semi_equipment_orders, hyperscaler_capex_signal,
    # electricity_demand_signal  — manually updated or via paid APIs
    print("    ~ Copper / Semi / Capex / Electricity: sample data (update manually or add paid API)")

    # ── Persist ──
    backup_snapshot(SNAPSHOT_PATH)
    validate_json_structure(snapshot, ["spy_price", "vix", "dxy", "tnx_yield"])
    atomic_write_json(snapshot, SNAPSHOT_PATH)

    print(f"  [Stage 1] Market snapshot saved → {SNAPSHOT_PATH}")
