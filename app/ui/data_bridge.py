import json
import os

def load_json_safe(path):
    if not os.path.exists(path):
        return {}
    with open(path) as f:
        return json.load(f)

def load_signals():
    raw = load_json_safe("data/processed/signal_snapshot.json")
    signals = raw.get("signals", [])
    # Return full objects to support tooltip explanations
    signals_list = [{"name": s["name"], "score": s["score"], "explanation": s.get("explanation", "")} for s in signals]
    return {"signals": signals_list}

def load_regime():
    raw = load_json_safe("macro_regime/regime_snapshot.json")
    regimes = raw.get("regimes", [])
    active_regime = ", ".join(regimes).replace("_", " ").title() if regimes else "Unknown"
    rationale = raw.get("regime_rationale", {})
    # Build history timeline
    history = []
    hist_dir = "data/history/regimes"
    if os.path.exists(hist_dir):
        for fname in sorted(os.listdir(hist_dir)):
            if fname.startswith("regime_snapshot_") and fname.endswith(".json"):
                 date_str = fname.replace("regime_snapshot_", "").replace(".json", "")
                 hist_data = load_json_safe(os.path.join(hist_dir, fname))
                 if hist_data and "regimes" in hist_data:
                     rgs = hist_data.get("regimes", [])
                     reg_name = rgs[0].replace("_", " ").title() if rgs else "Unknown" # taking first for simplicity in timeline
                     history.append({"date": date_str.replace("_", "-"), "regime": reg_name})
    
    return {"active_regime": active_regime, "history": history}

def load_portfolio():
    raw = load_json_safe("portfolio_model.json")
    engines = []
    for engine in raw.get("engines", []):
         engines.append({
             "name": engine["name"],
             "allocation_pct": engine["allocation_pct"],
             "rationale": engine.get("rationale", "No rationale provided by model.")
         })
    
    cash_pct = float(raw.get("cash_pct", 0))
    overall_rationale = raw.get("rationale", "No overall rationale provided.")
    
    return {
        "engines": engines,
        "cash_pct": cash_pct,
        "overall_rationale": overall_rationale,
        "stance": raw.get("stance", "neutral")
    }

def load_alerts():
    raw = load_json_safe("data/processed/alerts.json")
    out_alerts = []
    for a in raw.get("alerts", []):
         lvl = a.get("level", "WARNING")
         severity = "high" if lvl == "CRITICAL" else "medium"
         out_alerts.append({"severity": severity, "message": a.get("message", "")})
    return {"alerts": out_alerts}

def load_market_data():
    return load_json_safe("data/raw/market_snapshot.json")

def load_governance():
    raw = load_json_safe("decision_graph.json")
    passed = False
    violations = []
    
    for node in raw.get("nodes", []):
        if node.get("node_type") == "governance_node":
            meta = node.get("metadata", {})
            passed = meta.get("passed", False)
            violations = meta.get("violations", [])
            break
            
    return {
        "status": "passed" if passed else "failed",
        "violations": violations
    }
