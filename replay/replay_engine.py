"""
Antigravity — Replay Engine
Replays the pipeline deterministically using historical market snapshots.
Supports strategy comparison.
"""

import sys
import os
import json
import argparse
from datetime import datetime, timezone

# Ensure project root is in path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.models import MarketSnapshot
from app.signal_engine import score_signals
from app.macro_regime.regime_detector import detect_regime
from app.portfolio_engine import build_portfolio

def replay_pipeline(date: str, strategy: str = None):
    base = f"state/versions/{date}"
    
    market_path = os.path.join(base, "market_snapshot.json")
    if not os.path.exists(market_path):
        print(f"Error: Version state not found for {date} at {market_path}")
        return
        
    try:
        with open(market_path, "r", encoding="utf-8") as f:
            raw = json.load(f)
    except Exception as e:
        print(f"Error loading market snapshot: {e}")
        return

    print(f"--- Replaying Pipeline for {date} ---")
    snapshot = MarketSnapshot(**raw)
    
    # Rerun Signal Engine
    signal_snapshot = score_signals(snapshot)
    print(f"Signals Scored: {signal_snapshot.total_score:+.2f}")
    
    # Rerun Regime Detector
    macro_regime = detect_regime(signal_snapshot)
    print(f"Regimes Detected: {', '.join(macro_regime.regimes)}")
    
    # Rerun Portfolio Engine
    original_portfolio = build_portfolio(signal_snapshot, macro_regime)
    
    print("\nStrategy Comparison")
    print(f"\nOriginal Allocation (Stance: {original_portfolio.stance.upper()})")
    for engine in original_portfolio.engines:
        print(f"{engine.name}: {engine.allocation_pct:.0%}")
    print(f"Cash: {original_portfolio.cash_pct:.0%}")

    if strategy:
        print(f"\nAlternative Allocation ({strategy.upper()})")
        # Fake a macro regime to force the strategy
        macro_regime.regimes = [strategy]
        alt_portfolio = build_portfolio(signal_snapshot, macro_regime)
        for engine in alt_portfolio.engines:
            print(f"{engine.name}: {engine.allocation_pct:.0%}")
        print(f"Cash: {alt_portfolio.cash_pct:.0%}")
        
    _log_replay(date, strategy)

def _log_replay(date: str, strategy: str):
    log_path = "replay/replay_log.json"
    entry = {
        "date": date,
        "replay_run": datetime.now(timezone.utc).strftime("%Y_%m_%d"),
        "strategy_tested": strategy or "original",
        "result": "replay completed successfully"
    }
    
    log = []
    if os.path.exists(log_path):
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                log = json.load(f)
        except Exception:
            pass
            
    log.append(entry)
    with open(log_path, "w", encoding="utf-8") as f:
        json.dump(log, f, indent=2)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Antigravity Replay Engine")
    parser.add_argument("--date", required=True, help="Date format YYYY_MM_DD")
    parser.add_argument("--strategy", required=False, help="Alternative strategy/regime name")
    args = parser.parse_args()
    
    # Change working directory to ensure paths align with root
    os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    replay_pipeline(args.date, args.strategy)
