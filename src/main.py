import copy
import json
from pathlib import Path

from approval import can_deploy
from real_deployment import apply_managed_policy, MANAGED_FILE
from uuid import uuid4

from intents import validate_intent
from candidate_generator import generate_candidate
from approval import review_candidate
from deployment import deploy_candidate
from routers import routers
from audit_log import record_event
from wazuh_integration import deploy_approved_config


def run_workflow(intent, decision, simulate_failure=False):
    print("\n=== AIORI PS008 Network Management Agent ===")

    # Step 1: Validate intent
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

    # Step 2: Generate candidate
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

    # Step 3: Human approval
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

    if candidate["status"] != "APPROVED" or not success:
        print("Deployment blocked: candidate was not approved.")
        return candidate, message

    # Step 4: Simulated deployment
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

    # Step 5: Wazuh integration
    # Publish only after successful simulated deployment.
    if success and candidate["status"] == "DEPLOYED":
        change_id = f"PS008-{uuid4().hex[:8].upper()}"

        try:
            artifact = deploy_approved_config(
                change_id=change_id,
                reviewer=candidate.get("reviewer") or reviewer,
                config=candidate["proposed"],
                approved=True,
            )

            print(
                "5. Wazuh artifact published:",
                artifact["change_id"],
            )

        except (OSError, ValueError) as error:
            print("5. Wazuh artifact publication failed:", error)

            record_event(
                event="WAZUH_ARTIFACT_PUBLICATION_FAILED",
                router=candidate["router"],
                reviewer=reviewer,
                details={
                    "change_id": change_id,
                    "error": str(error),
                },
            )
    else:
        print("5. Wazuh publication skipped: no successful deployment.")

    return candidate, message

def run_managed_policy_workflow(decision, reviewer, simulate_failure=False):
    """
    Demonstrate reviewed deployment to a Wazuh-monitored policy file.
    Does not modify live network interfaces or routing.
    """

    print("\n=== PS008 MANAGED POLICY WORKFLOW ===")

    current = json.loads(MANAGED_FILE.read_text(encoding="utf-8"))
    proposed = copy.deepcopy(current)

    proposed["policy_version"] = current["policy_version"] + 1
    proposed["description"] = (
        f"PS008 reviewed policy version {proposed['policy_version']}"
    )

    candidate = {
        "router": current["router"],
        "before": copy.deepcopy(current),
        "proposed": copy.deepcopy(proposed),
        "proposed_policy": copy.deepcopy(proposed),
        "status": "PENDING_REVIEW",
    }

    print("1. Current policy version:", current["policy_version"])
    print("2. Proposed policy:")
    print(json.dumps(proposed, indent=4))

    success, message = review_candidate(
        candidate,
        decision=decision,
        reviewer=reviewer,
    )

    print("3. Human review:", message)

    record_event(
        event="MANAGED_POLICY_APPROVAL",
        router=candidate["router"],
        reviewer=reviewer,
        details={
            "decision": decision,
            "status": candidate["status"],
            "message": message,
        },
    )

    if not success or not can_deploy(candidate):
        print("4. Deployment blocked: approval required.")
        return candidate, False

    deployed, result = apply_managed_policy(
        candidate,
        proposed,
        simulate_failure=simulate_failure,
    )

    print("4. Managed policy deployment:", result)

    if deployed:
        candidate["status"] = "DEPLOYED"
    else:
        candidate["status"] = "DEPLOYMENT_FAILED"

    print("5. Final candidate status:", candidate["status"])
    print(
        "6. Active policy version:",
        json.loads(MANAGED_FILE.read_text(encoding="utf-8"))["policy_version"],
    )

    return candidate, deployed



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
