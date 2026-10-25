from intents import validate_intent
from candidate_generator import generate_candidate
from approval import review_candidate
from deployment import deploy_candidate
from routers import routers
from audit_log import record_event


def run_workflow(intent, decision, simulate_failure=False):
    print("\n=== AIORI PS008 Network Management Agent ===")

    # Step 1: Validate the operator's intent.
    valid, message = validate_intent(intent)

    record_event(
        event="INTENT_VALIDATED" if valid else "INTENT_REJECTED",
        router=intent.get("router"),
        details={
            "intent_type": intent.get("type"),
            "message": message,
        },
    )

    if not valid:
        print("1. Intent validation:", message)
        return None, message

    print("1. Intent validation:", message)

    # Step 2: Generate a candidate configuration.
    candidate, message = generate_candidate(intent)
    print("2. Candidate generation:", message)

    if candidate is None:
        record_event(
            event="CANDIDATE_REJECTED",
            router=intent.get("router"),
            details={
                "intent_type": intent.get("type"),
                "message": message,
            },
        )
        return None, message

    print("   Status:", candidate["status"])

    record_event(
        event="CANDIDATE_GENERATED",
        router=candidate["router"],
        details={
            "status": candidate["status"],
            "intent_type": intent.get("type"),
        },
    )

    # Step 3: Request a human review decision.
    reviewer = "demo-reviewer"

    success, message = review_candidate(
        candidate,
        decision=decision,
        reviewer=reviewer,
    )

    print("3. Human review:", message)

    record_event(
        event="APPROVAL_DECISION",
        router=candidate["router"],
        reviewer=reviewer,
        details={
            "decision": decision,
            "status": candidate["status"],
            "message": message,
        },
    )
    # Stop immediately if the candidate was not approved.
    if candidate["status"] != "APPROVED":
        print("Deployment blocked: candidate was not approved.")
        return candidate, message

    # Also stop if the review operation itself reports failure.
    if not success:
        print("Deployment blocked: the review operation failed.")
        return candidate, message

    # Step 4: Deploy only if approved.
    success, message = deploy_candidate(
        candidate,
        simulate_failure=simulate_failure,
    )

    print("4. Deployment:", message)
    print("   Final status:", candidate["status"])

    record_event(
        event=candidate["status"],
        router=candidate["router"],
        reviewer=reviewer,
        details={
            "message": message,
            "success": success,
        },
    )

    return candidate, message



if __name__ == "__main__":
    # Demo 1: Successful deployment
    successful_intent = {
        "type": "change_interface_ip",
        "router": "R1",
        "interface": "eth0",
        "new_ip": "10.0.12.10/24",
    }

    print("\n========== DEMO 1: SUCCESSFUL DEPLOYMENT ==========")
    print("Initial R1 configuration:", routers["R1"])

    run_workflow(
        intent=successful_intent,
        decision="approve",
        simulate_failure=False,
    )

    print("Final R1 configuration:", routers["R1"])

    # Demo 2: Failed deployment with rollback
    rollback_intent = {
        "type": "change_interface_ip",
        "router": "R1",
        "interface": "eth0",
        "new_ip": "10.0.12.20/24",
    }

    print("\n========== DEMO 2: DEPLOYMENT FAILURE AND ROLLBACK ==========")
    print("Initial R1 configuration:", routers["R1"])

    run_workflow(
        intent=rollback_intent,
        decision="approve",
        simulate_failure=True,
    )

    print("Final R1 configuration:", routers["R1"])
