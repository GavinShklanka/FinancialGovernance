"""
Antigravity — Education engine.

Translates raw signal scores into plain‑language explanations
so the reader understands *why* each signal matters.
"""

from app.models import SignalSnapshot


_EXPLANATIONS = {
    "VIX Level": (
        "The VIX measures expected 30‑day volatility of the S&P 500. "
        "A low VIX (< 15) suggests calm markets and bullish sentiment, "
        "while a high VIX (> 25) reflects fear and uncertainty."
    ),
    "DXY Strength": (
        "The DXY index tracks the US dollar against a basket of major currencies. "
        "A strong dollar (> 105) tends to weigh on commodities and emerging‑market "
        "equities, while a weak dollar supports them."
    ),
    "10Y Yield": (
        "The US 10‑year Treasury yield reflects long‑term interest rate expectations. "
        "Rising yields increase the cost of capital, pressuring high‑growth and "
        "duration‑sensitive assets."
    ),
    "Gold Momentum": (
        "Gold is a traditional safe‑haven asset. Elevated prices (> $2 100) often "
        "indicate risk‑off hedging activity and inflation concerns."
    ),
    "BTC Momentum": (
        "Bitcoin serves as a barometer for risk appetite in digital assets. "
        "Prices above $60 000 typically correlate with broader risk‑on sentiment."
    ),
}


def build_education_notes(signal_snapshot: SignalSnapshot) -> list:
    """Return a list of educational strings, one per signal."""

    notes = []

    for signal in signal_snapshot.signals:
        explanation = _EXPLANATIONS.get(signal.name, "No additional context available.")

        direction = "bullish" if signal.score > 0 else ("bearish" if signal.score < 0 else "neutral")

        note = (
            f"**{signal.name}** — current value {signal.value}, "
            f"scored {signal.score:+.1f} ({direction}).\n"
            f"  {explanation}"
        )
        notes.append(note)

    return notes
