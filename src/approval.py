
from datetime import datetime, timezone


def review_candidate(candidate, decision, reviewer):
    """Record a human decision on a proposed configuration."""

    if not isinstance(candidate, dict):
        return False, "Invalid candidate."

    if candidate.get("status") != "PENDING_REVIEW":
        return False, "Candidate is not awaiting review."

    if not isinstance(reviewer, str) or not reviewer.strip():
        return False, "Reviewer identity is required."

    if decision not in ("approve", "reject"):
        return False, "Decision must be approve or reject."

    if not candidate.get("before") or not candidate.get("proposed"):
        return False, "Candidate configuration is missing."

    if decision == "approve":
        candidate["status"] = "APPROVED"
    else:
        candidate["status"] = "REJECTED"

    candidate["reviewer"] = reviewer.strip()
    candidate["reviewed_at"] = datetime.now(timezone.utc).isoformat()

    return True, f"Candidate {candidate['status']} by {reviewer}."


def can_deploy(candidate):
    """Only an approved candidate may proceed to deployment."""

    return (
        isinstance(candidate, dict)
        and candidate.get("status") == "APPROVED"
        and bool(candidate.get("reviewer"))
        and bool(candidate.get("reviewed_at"))
    )


if __name__ == "__main__":
    candidate = {
        "router": "R1",
        "before": {"interfaces": {"eth0": "10.0.12.1/24"}},
        "proposed": {"interfaces": {"eth0": "10.0.12.10/24"}},
        "status": "PENDING_REVIEW",
    }

    print("Before review:", candidate["status"])

    success, message = review_candidate(
        candidate,
        decision="reject",
        reviewer="mentor"
    )

    print(message)
    print("Can proceed to deployment:", can_deploy(candidate))
