"""
Antigravity — Signal Persistence Analysis
Analyzes signals across historical states to identify structural macro trends.
"""

import os
import json
import glob

STATE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "state", "versions")

def analyze_persistence(signal_name: str):
    patterns = os.path.join(STATE_DIR, "*", "signal_snapshot.json")
    files = glob.glob(patterns)
    
    active_weeks = 0
    total_score = 0.0
    
    for fpath in files:
        try:
            with open(fpath, "r", encoding="utf-8") as f:
                data = json.load(f)
                
            for sig in data.get("signals", []):
                if sig.get("name") == signal_name:
                    active_weeks += 1
                    total_score += sig.get("score", 0.0)
        except Exception:
            continue

    if active_weeks > 0:
        avg_score = total_score / active_weeks
        persistence = "High" if active_weeks >= 4 else "Moderate" if active_weeks >= 2 else "Low"
        
        print(f"{signal_name} Bullish Signal")
        print(f"Active Weeks: {active_weeks}")
        print(f"Average Score: {avg_score:+.1f}")
        print(f"Persistence: {persistence}")
    else:
        print(f"No historical data for signal: {signal_name}")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1:
        analyze_persistence(sys.argv[1])
    else:
        analyze_persistence("Copper Inventories")
