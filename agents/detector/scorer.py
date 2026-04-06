"""
Layer 2: Weighted Scorer
Converts flags into a risk score 0-100.
Pure math. No AI.

Score = sum of triggered weights, capped at 100.
Each weight is calibrated so that:
  - Velocity alone → 80 (REJECTED)
  - Amount deviation alone → 35 (REVIEW)
  - New account + high first transaction → 40 (REVIEW)
"""

FLAG_WEIGHTS = {
    "Amount":                        35,
    "unfamiliar location":           25,
    "unusual hour":                  15,
    "High-risk merchant":            15,
    "Velocity":                      80,
    "New account":                   10,
    "Foreign transaction":           20,
    "High absolute amount":          10,
    "High transaction for new account": 30,
}

VERDICT_THRESHOLDS = [
    (70, "REJECTED"),
    (31, "REVIEW"),
    (0,  "APPROVED"),
]


def calculate_score(flags: list[str]) -> int:
    total = 0
    for flag in flags:
        for keyword, weight in FLAG_WEIGHTS.items():
            if keyword in flag:
                total += weight
                break
    return min(100, total)


def get_verdict(score: int) -> str:
    for threshold, verdict in VERDICT_THRESHOLDS:
        if score >= threshold:
            return verdict
    return "APPROVED"
