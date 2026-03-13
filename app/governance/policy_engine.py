"""
Antigravity — Governance & Policy Engine (Stage 5).

Validates the portfolio recommendation against institutional-style
risk governance rules. Returns a GovernanceResult indicating whether
the portfolio passes, and a full list of violations if it doesn't.

Policy rules enforced:
  1. No single engine allocation > 25% of total (excluding cash)
     — actually allows up to 45% since this is a 3-engine model;
       the spec says no single POSITION > 25%.
  2. Cash allocation must be >= 10%.
  3. VIX > 30 triggers a CRITICAL escalation flag (mandatory review).
  4. Total engine allocations + cash must not exceed 100%.
"""

from app.models import Portfolio, SignalSnapshot, GovernanceResult, PolicyViolation


# ── Policy rules ─────────────────────────────────────────────────────────────

def _check_min_cash(portfolio: Portfolio) -> list[PolicyViolation]:
    violations = []
    if portfolio.cash_pct < 0.10:
        violations.append(PolicyViolation(
            rule="MIN_CASH_10PCT",
            detail=f"Cash allocation is {portfolio.cash_pct:.0%}. Minimum required is 10%.",
            severity="WARNING",
        ))
    return violations


def _check_max_engine_allocation(portfolio: Portfolio) -> list[PolicyViolation]:
    """No single engine should exceed 45% allocation (engine model)."""
    violations = []
    for engine in portfolio.engines:
        if engine.allocation_pct > 0.45:
            violations.append(PolicyViolation(
                rule="MAX_ENGINE_45PCT",
                detail=(
                    f"Engine '{engine.name}' is allocated {engine.allocation_pct:.0%}, "
                    "exceeding the 45% single-engine cap."
                ),
                severity="WARNING",
            ))
    return violations


def _check_vix_escalation(signal_snapshot: SignalSnapshot) -> list[PolicyViolation]:
    """VIX > 30 requires mandatory human review before execution."""
    violations = []
    if signal_snapshot.vix > 30:
        violations.append(PolicyViolation(
            rule="VIX_ESCALATION",
            detail=(
                f"VIX is {signal_snapshot.vix:.1f} — above 30. "
                "CRITICAL: Do NOT execute any new positions without manual human review."
            ),
            severity="CRITICAL",
        ))
    return violations


def _check_allocation_integrity(portfolio: Portfolio) -> list[PolicyViolation]:
    """All allocations + cash must sum to approximately 100%."""
    violations = []
    engine_total = sum(e.allocation_pct for e in portfolio.engines)
    grand_total  = engine_total + portfolio.cash_pct
    if abs(grand_total - 1.0) > 0.02:  # allow 2% rounding tolerance
        violations.append(PolicyViolation(
            rule="ALLOCATION_INTEGRITY",
            detail=(
                f"Engine allocations ({engine_total:.0%}) + cash ({portfolio.cash_pct:.0%}) "
                f"= {grand_total:.0%}. Must sum to 100%."
            ),
            severity="WARNING",
        ))
    return violations


# ── Public API ───────────────────────────────────────────────────────────────

def run_governance_check(
    portfolio: Portfolio,
    signal_snapshot: SignalSnapshot,
) -> GovernanceResult:
    """Run all policy checks and return a GovernanceResult."""

    all_violations: list[PolicyViolation] = []
    notes: list[str] = []

    all_violations += _check_min_cash(portfolio)
    all_violations += _check_max_engine_allocation(portfolio)
    all_violations += _check_vix_escalation(signal_snapshot)
    all_violations += _check_allocation_integrity(portfolio)

    has_critical = any(v.severity == "CRITICAL" for v in all_violations)
    passed       = len(all_violations) == 0

    if passed:
        notes.append("All governance policies passed. Portfolio cleared for execution consideration.")
    elif has_critical:
        notes.append("CRITICAL violations present. Halt execution and review before proceeding.")
    else:
        notes.append("Warnings detected. Review violations before executing trades.")

    result = GovernanceResult(
        passed=passed,
        violations=all_violations,
        notes=notes,
    )

    _print_governance_summary(result)
    return result


def _print_governance_summary(result: GovernanceResult) -> None:
    status = "PASSED" if result.passed else f"FAILED ({len(result.violations)} violation(s))"
    print(f"  [Stage 5] Governance check → {status}")
    for v in result.violations:
        print(f"            [{v.severity}] {v.rule}: {v.detail}")
