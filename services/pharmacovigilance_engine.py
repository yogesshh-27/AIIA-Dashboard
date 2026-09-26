"""
WHO-Standard Pharmacovigilance Disproportionality Engine
Calculates Proportional Reporting Ratio (PRR) and Reporting Odds Ratio (ROR)
with 95% Confidence Intervals and Yates' Chi-Squared statistical test.
Adheres to Evans et al. (2001) and WHO criteria for safety signal detection.
"""

import math
from typing import Dict, List, Any


def calculate_disproportionality_metrics(a: int, b: int, c: int, d: int) -> Dict[str, Any]:
    """
    Given a 2x2 contingency table:
      - a: cases with Target Drug & Target Event
      - b: cases with Target Drug & Other Events
      - c: cases with Other Drugs & Target Event
      - d: cases with Other Drugs & Other Events

    Calculates:
      - PRR = [a / (a + b)] / [c / (c + d)]
      - PRR 95% CI
      - ROR = (a * d) / (b * c)
      - ROR 95% CI
      - Yates' Chi-squared
      - WHO / Evans signal criteria determination
    """
    n = a + b + c + d
    if n == 0 or (a + b) == 0 or (c + d) == 0 or (a + c) == 0 or (b + d) == 0:
        return {
            "a": a, "b": b, "c": c, "d": d,
            "prr": 0.0, "prr_ci_lower": 0.0, "prr_ci_upper": 0.0,
            "ror": 0.0, "ror_ci_lower": 0.0, "ror_ci_upper": 0.0,
            "chi2_yates": 0.0,
            "is_signal": False,
            "confidence": "Insufficient Data"
        }

    # Add small continuity correction if zero cell exists to prevent div by zero
    adj_a = a if a > 0 else 0.5
    adj_b = b if b > 0 else 0.5
    adj_c = c if c > 0 else 0.5
    adj_d = d if d > 0 else 0.5

    # 1. Proportional Reporting Ratio (PRR)
    prr = (adj_a / (adj_a + adj_b)) / (adj_c / (adj_c + adj_d))
    try:
        se_ln_prr = math.sqrt((1.0 / adj_a) - (1.0 / (adj_a + adj_b)) + (1.0 / adj_c) - (1.0 / (adj_c + adj_d)))
        prr_lower = math.exp(math.log(prr) - 1.96 * se_ln_prr)
        prr_upper = math.exp(math.log(prr) + 1.96 * se_ln_prr)
    except (ValueError, ZeroDivisionError):
        prr_lower, prr_upper = 0.0, 0.0

    # 2. Reporting Odds Ratio (ROR)
    ror = (adj_a * adj_d) / (adj_b * adj_c)
    try:
        se_ln_ror = math.sqrt((1.0 / adj_a) + (1.0 / adj_b) + (1.0 / adj_c) + (1.0 / adj_d))
        ror_lower = math.exp(math.log(ror) - 1.96 * se_ln_ror)
        ror_upper = math.exp(math.log(ror) + 1.96 * se_ln_ror)
    except (ValueError, ZeroDivisionError):
        ror_lower, ror_upper = 0.0, 0.0

    # 3. Yates' Chi-squared
    numerator = max(0, abs(a * d - b * c) - (n / 2.0)) ** 2 * n
    denominator = (a + b) * (c + d) * (a + c) * (b + d)
    chi2 = (numerator / denominator) if denominator > 0 else 0.0

    # 4. Evans et al. criteria for signal detection:
    # (a) >= 3 cases
    # (b) PRR >= 2.0
    # (c) Chi-squared >= 4.0
    is_evans_signal = (a >= 3) and (prr >= 2.0) and (chi2 >= 4.0)

    # Secondary WHO ROR criterion: lower 95% CI of ROR > 1.0
    is_ror_signal = (a >= 3) and (ror_lower > 1.0)

    is_signal = is_evans_signal or is_ror_signal

    if is_evans_signal and prr_lower > 1.2:
        confidence = "High (Confirmed Signal)"
    elif is_signal or (a >= 2 and prr >= 2.0):
        confidence = "Medium (Emerging Signal)"
    elif a >= 1 and prr >= 1.5:
        confidence = "Low (Under Observation)"
    else:
        confidence = "Normal / Expected Variation"

    return {
        "a": a,
        "b": b,
        "c": c,
        "d": d,
        "prr": round(prr, 2),
        "prr_ci_lower": round(prr_lower, 2),
        "prr_ci_upper": round(prr_upper, 2),
        "ror": round(ror, 2),
        "ror_ci_lower": round(ror_lower, 2),
        "ror_ci_upper": round(ror_upper, 2),
        "chi2_yates": round(chi2, 2),
        "is_signal": bool(is_signal),
        "evans_criteria_met": bool(is_evans_signal),
        "confidence": confidence
    }


def analyze_dataset_signals(adverse_events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Scans a list of adverse event dictionaries and detects all drug-reaction pair signals.
    """
    if not adverse_events:
        return []

    # Map pairs
    # Standardize treatment and reaction terms
    reports = []
    for ev in adverse_events:
        treatment = (ev.get("suspected_treatment") or ev.get("treatment") or "Unknown").strip()
        reaction = (ev.get("adverse_event") or ev.get("event_term") or "Unknown").strip()
        reports.append((treatment, reaction, ev))

    all_treatments = set(t for t, r, ev in reports)
    all_reactions = set(r for t, r, ev in reports)

    detected_signals = []

    for treatment in all_treatments:
        for reaction in all_reactions:
            # Build contingency table
            a = sum(1 for t, r, _ in reports if t == treatment and r == reaction)
            if a == 0:
                continue

            b = sum(1 for t, r, _ in reports if t == treatment and r != reaction)
            c = sum(1 for t, r, _ in reports if t != treatment and r == reaction)
            d = sum(1 for t, r, _ in reports if t != treatment and r != reaction)

            metrics = calculate_disproportionality_metrics(a, b, c, d)

            if metrics["is_signal"] or metrics["confidence"] in ["High (Confirmed Signal)", "Medium (Emerging Signal)"]:
                detected_signals.append({
                    "suspected_treatment": treatment,
                    "adverse_event": reaction,
                    "case_count": a,
                    **metrics,
                    "recommendation": (
                        f"Statistical disproportionality detected for {treatment} and {reaction} "
                        f"(PRR: {metrics['prr']} [95% CI {metrics['prr_ci_lower']}-{metrics['prr_ci_upper']}], "
                        f"ROR: {metrics['ror']}, Chi²: {metrics['chi2_yates']}). "
                        "Immediate review by DSMB and Pharmacovigilance Committee recommended."
                    )
                })

    # Sort by PRR and case count descending
    detected_signals.sort(key=lambda s: (s["prr"], s["case_count"]), reverse=True)
    return detected_signals
