"""
Antigravity Master Script — run_antigravity_cycle.py

Orchestrates the full 8-stage macro investment intelligence pipeline.

Usage:
    python antigravity/run_antigravity_cycle.py

Stages:
    1. Fetch market data          → data/raw/market_snapshot.json
    2. Score signals              → data/processed/signal_snapshot.json
    3. Detect macro regime        → macro_regime/regime_snapshot.json
    4. Build portfolio model      → portfolio_model.json
    5. Run governance checks      → (inline — flagged violations printed)
    6. Record decision graph      → decision_graph.json
    7. Build Claude prompt        → app/outputs/claude_prompt.txt
    8. Generate weekly report     → app/outputs/weekly_report.md

Requires: .env with at minimum FRED_API_KEY and ALPHAVANTAGE_API_KEY for live data.
          Falls back to sample data if keys are absent.
"""

import sys
import os
import shutil

# ── Load environment first ───────────────────────────────────────────────────
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    print("[WARN] python-dotenv not installed. Run: pip install python-dotenv")
    print("       Keys must be set as environment variables manually.")

# ── Imports ───────────────────────────────────────────────────────────────────
from datetime import datetime, timezone

from app.data.fetch_market_data import fetch_and_store_market_snapshot
from app.data.loaders import load_json

from app.models import MarketSnapshot
from app.signal_engine import score_signals
from app.macro_regime.regime_detector import detect_regime
from app.portfolio_engine import build_portfolio
from app.governance.policy_engine import run_governance_check
from app.claude_prompt_builder import build_claude_prompt
from app.report_engine import generate_report, save_report
from app.alerts.alert_engine import generate_alerts
from app.data.cache_engine import save_cache
from app.data.loaders import load_json

from app.reporting.portfolio_evaluator import evaluate_portfolio
from app.reporting.exporters import export_json as export_eval_json, export_markdown as export_eval_md

from system_integrity.recovery_manager import restore_backup
from system_integrity.state_manager import create_state_snapshot
from decision_graph.decision_graph_builder import DecisionGraphBuilder, GraphStore


# ── Rich console output (graceful fallback) ───────────────────────────────────
try:
    from rich.console import Console
    from rich.panel import Panel
    from rich.rule import Rule
    _console = Console()
    def _banner(text: str) -> None:
        _console.print(Rule(f"[bold cyan]{text}[/bold cyan]"))
    def _done(text: str) -> None:
        _console.print(f"  [green]✓[/green] {text}")
except ImportError:
    def _banner(text: str) -> None:
        print(f"\n{'='*60}")
        print(f"  {text}")
        print(f"{'='*60}")
    def _done(text: str) -> None:
        print(f"  ✓ {text}")


# ── Pipeline ──────────────────────────────────────────────────────────────────

def run_antigravity_cycle() -> None:

    start_time = datetime.now(timezone.utc)
    _banner("🛰  ANTIGRAVITY — Starting Full 8-Stage Pipeline")
    print(f"  Cycle started at: {start_time.strftime('%Y-%m-%d %H:%M UTC')}\n")

    # ── System Integrity Check ──────────────────────────────────
    _banner("System Integrity Check / Crash Recovery")
    snapshots = [
        "data/raw/market_snapshot.json",
        "data/processed/signal_snapshot.json",
        "macro_regime/regime_snapshot.json",
        "portfolio_model.json",
        "decision_graph.json"
    ]
    for snap in snapshots:
        if os.path.exists(snap):
            try:
                load_json(snap)
                print(f"  [OK] Validated {snap}")
            except Exception:
                print(f"  [WARN] Corruption detected in {snap}. Restoring backup...")
                restore_backup(snap)
                
    # ── Stage 1: Data Ingestion ──────────────────────────────────
    _banner("Stage 1 — Market Data Ingestion")
    fetch_and_store_market_snapshot()

    raw = load_json("data/raw/market_snapshot.json")
    snapshot = MarketSnapshot(**raw)
    _done("Market snapshot loaded.")

    # ── Stage 1.5: Alert Engine ────────────────────────────────
    _banner("Stage 1.5 — Alert Engine")
    alerts = generate_alerts(snapshot)
    _done(f"{len(alerts)} alerts generated.")

    # ── Stage 2: Signal Engine ───────────────────────────────────
    _banner("Stage 2 — Signal Engine")
    signal_snapshot = score_signals(snapshot)
    _done(f"Signals scored. Total weighted score: {signal_snapshot.total_score:+.2f}")

    # ── Stage 3: Macro Regime Detector ───────────────────────────
    _banner("Stage 3 — Macro Regime Detector")
    macro_regime = detect_regime(signal_snapshot)
    _done(f"Regimes: {', '.join(macro_regime.regimes)}")

    # ── Stage 4: Portfolio Engine ────────────────────────────────
    _banner("Stage 4 — Portfolio Engine (Three-Engine Model)")
    portfolio = build_portfolio(signal_snapshot, macro_regime)
    _done(f"Portfolio built. Stance: {portfolio.stance.upper()}")

    # ── Stage 5: Governance & Policy Check ──────────────────────
    _banner("Stage 5 — Governance & Policy Check")
    governance = run_governance_check(portfolio, signal_snapshot)
    if governance.passed:
        _done("All policies passed.")
    else:
        print(f"  ⚠  {len(governance.violations)} violation(s) detected — review before execution.")

    # ── Stage 5.5: Portfolio Evaluation Report ────────────────────
    _banner("Stage 5.5 — Portfolio Evaluation Report")
    eval_report = evaluate_portfolio(signal_snapshot, macro_regime, portfolio, governance)
    export_eval_json(eval_report)
    export_eval_md(eval_report)
    _done(f"Evaluation: {eval_report.simple_summary}")

    # ── Stage 6: Decision Graph ──────────────────────────────────
    _banner("Stage 6 — Decision Graph Recording")
    nodes = DecisionGraphBuilder.build_cycle_graph(
        signal_score=signal_snapshot.total_score,
        regimes=macro_regime.regimes,
        portfolio_stance=portfolio.stance,
        governance_passed=governance.passed,
    )
    store = GraphStore()
    store.save_cycle_graph(nodes)
    _done(f"Decision graph recorded ({len(nodes)} nodes).")

    # ── Stage 7: Claude Prompt Builder ──────────────────────────
    _banner("Stage 7 — AI Research Layer (Claude Prompt)")
    build_claude_prompt(signal_snapshot, macro_regime, portfolio, governance)
    _done("Claude master prompt generated → app/outputs/claude_prompt.txt")

    # ── Stage 8: Report ──────────────────────────────────────────
    _banner("Stage 8 — Weekly Report")
    report = generate_report(
        signal_snapshot=signal_snapshot,
        portfolio=portfolio,
        macro_regime=macro_regime,
        governance=governance,
    )
    save_report(report)
    _done("Weekly report generated → app/outputs/weekly_report.md")

    # ── Historical Persistence ──────────────────────────────────
    _banner("Historical Persistence")
    date_str = start_time.strftime("%Y_%m_%d")
    
    os.makedirs("data/history/signals", exist_ok=True)
    os.makedirs("data/history/regimes", exist_ok=True)
    os.makedirs("data/history/portfolio", exist_ok=True)

    shutil.copy("data/processed/signal_snapshot.json", f"data/history/signals/signal_snapshot_{date_str}.json")
    shutil.copy("macro_regime/regime_snapshot.json", f"data/history/regimes/regime_snapshot_{date_str}.json")
    shutil.copy("portfolio_model.json", f"data/history/portfolio/portfolio_{date_str}.json")

    # Generate dashboard cache
    performance_series = {
        "timestamp": start_time.strftime("%Y-%m-%d %H:%M:%S"),
        "total_score": signal_snapshot.total_score,
        "stance": portfolio.stance,
        "cash_pct": portfolio.cash_pct,
        "regimes": macro_regime.regimes
    }
    save_cache("performance_series", performance_series, cache_type="dashboard")

    # ── State Versioning ──────────────────────────────────────────
    _banner("State Versioning")
    create_state_snapshot(
        signal_score=signal_snapshot.total_score,
        regimes=macro_regime.regimes,
        portfolio_stance=portfolio.stance
    )
    _done("State saved to versioned folder.")

    # ── Summary ──────────────────────────────────────────────────
    elapsed = (datetime.now(timezone.utc) - start_time).total_seconds()
    _banner(f"✅  Pipeline Complete ({elapsed:.1f}s)")
    print()
    print("  Output files:")
    print("    data/raw/market_snapshot.json")
    print("    data/processed/signal_snapshot.json")
    print("    macro_regime/regime_snapshot.json")
    print("    portfolio_model.json")
    print("    decision_graph.json")
    print("    app/outputs/claude_prompt.txt")
    print("    app/outputs/weekly_report.md")
    print("    data/processed/reports/latest_portfolio_evaluation.json")
    print("    data/processed/reports/latest_portfolio_evaluation.md")
    print()
    print("  Next step: open app/outputs/claude_prompt.txt → paste into Claude.")
    print()


if __name__ == "__main__":
    # Change working directory to antigravity/ so relative paths resolve
    script_dir = os.path.dirname(os.path.abspath(__file__))
    os.chdir(script_dir)
    run_antigravity_cycle()
