import hashlib
import hmac
import json
from datetime import datetime, timezone


def _candidate_fingerprint(candidate):
    """Create a fingerprint of the candidate configuration and router."""

    approved_data = {
        "router": candidate.get("router"),
        "before": candidate.get("before"),
        "proposed": candidate.get("proposed"),
    }

    serialized = json.dumps(
        approved_data,
        sort_keys=True,
        separators=(",", ":"),
    )

    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


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

    if not isinstance(candidate.get("before"), dict):
        return False, "Candidate's original configuration is invalid."

    if not isinstance(candidate.get("proposed"), dict):
        return False, "Candidate's proposed configuration is invalid."

    if not isinstance(candidate.get("router"), str):
        return False, "Candidate router is invalid."

    if decision == "approve":
        candidate["approved_fingerprint"] = _candidate_fingerprint(
            candidate
        )
        candidate["status"] = "APPROVED"
    else:
        candidate["status"] = "REJECTED"

    candidate["reviewer"] = reviewer.strip()
    candidate["reviewed_at"] = datetime.now(timezone.utc).isoformat()

    return True, f"Candidate {candidate['status']} by {reviewer}."


def can_deploy(candidate):
    """Check approval and detect candidate modifications after review."""

    if not isinstance(candidate, dict):
        return False

    if candidate.get("status") != "APPROVED":
        return False

    if not isinstance(candidate.get("reviewer"), str):
        return False

    if not candidate["reviewer"].strip():
        return False

    if not candidate.get("reviewed_at"):
        return False

    approved_fingerprint = candidate.get("approved_fingerprint")

    if not isinstance(approved_fingerprint, str):
        return False

    try:
        current_fingerprint = _candidate_fingerprint(candidate)
    except (TypeError, ValueError):
        return False

    return hmac.compare_digest(
        approved_fingerprint,
        current_fingerprint,
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
        decision="approve",
        reviewer="mentor",
    )

    print(message)
    print("Can proceed to deployment:", can_deploy(candidate))