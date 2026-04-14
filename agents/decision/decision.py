from tools.llm_router import call_llm
from tools.logger import get_logger

logger = get_logger("DECISION")


def decide(detector: dict, investigator: dict) -> dict:
    detector_score = detector["detector_score"]
    investigator_deviation = investigator["investigator_deviation"]

    # Step 1 — Combined score
    combined = (detector_score * 0.6) + (investigator_deviation * 0.4)

    # Step 2 — Final verdict
    if combined >= 70:
        verdict = "REJECTED"
    elif combined >= 40:
        verdict = "REVIEW"
    else:
        verdict = "APPROVED"

    # Step 3 — Confidence
    if combined >= 85 or combined <= 15:
        confidence = 95
    elif combined >= 70 or combined <= 30:
        confidence = 85
    elif combined >= 50:
        confidence = 70
    else:
        confidence = 60

    logger.info(f"verdict: {verdict} | combined: {combined:.0f} | confidence: {confidence}")

    # Step 4 — LLM reasoning
    flags = ", ".join(detector.get("detector_flags", []))
    investigator_summary = investigator.get("investigator_summary", "")

    prompt = f"""You are a senior fraud analyst. Write a structured decision report.

Transaction risk data:
- Detector score: {detector_score}/100
- Triggered flags: {flags}
- Behavioural deviation: {investigator_deviation}/100
- Behavioural analysis: {investigator_summary}
- Combined fraud score: {combined:.0f}/100
- Verdict: {verdict}

Respond in exactly this format, no markdown, no bullet symbols:

DECISION: [one sentence verdict summary]
SIGNALS: [one sentence listing the key flags that drove this]
BEHAVIOUR: [one sentence on what the behavioural analysis shows]
ACTION: [one sentence on what the analyst should do next]"""

    reason = call_llm(prompt)

    return {
        "verdict": verdict,
        "confidence": confidence,
        "reason": reason,
        "combined_score": combined,
    }


if __name__ == "__main__":
    detector = {
        "detector_score": 65,
        "detector_flags": ["crypto", "nigeria"],
        "detector_verdict": "REVIEW",
    }
    investigator = {
        "investigator_deviation": 60,
        "investigator_summary": "Amount 53x normal, new country",
    }
    result = decide(detector, investigator)
    print(result)
