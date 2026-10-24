import copy

from routers import routers
from approval import can_deploy


def deploy_candidate(candidate, simulate_failure=False):
    """
    Deploy an approved candidate configuration.

    Verify the deployment and restore the previous configuration
    if deployment or verification fails.
    """

    # Step 1: Verify human approval.
    if not can_deploy(candidate):
        return False, "Deployment blocked: human approval is required."

    router_name = candidate.get("router")

    # Step 2: Verify that the router exists.
    if router_name not in routers:
        return False, "Deployment failed: unknown router."

    # Step 3: Verify that the current configuration has not changed.
    if routers[router_name] != candidate.get("before"):
        return False, (
            "Deployment blocked: current configuration has changed."
        )

    # Step 4: Save the previous configuration for rollback.
    previous_config = copy.deepcopy(routers[router_name])
    proposed_config = copy.deepcopy(candidate.get("proposed"))

    if not isinstance(proposed_config, dict):
        return False, "Deployment failed: invalid proposed configuration."

    try:
        # Step 5: Apply the proposed configuration.
        routers[router_name] = copy.deepcopy(proposed_config)

        # Step 6: Simulate a deployment or verification failure.
        if simulate_failure:
            raise RuntimeError("Simulated deployment verification failure.")

        # Step 7: Verify the applied configuration.
        if routers[router_name] != proposed_config:
            raise RuntimeError("Applied configuration does not match proposal.")

        # Step 8: Mark deployment as successful.
        candidate["status"] = "DEPLOYED"

        return True, f"Deployment successful on {router_name}."

    except Exception as error:
        # Step 9: Restore the previous configuration.
        routers[router_name] = copy.deepcopy(previous_config)

        # Step 10: Verify that rollback succeeded.
        if routers[router_name] == previous_config:
            candidate["status"] = "ROLLED_BACK"
            return False, (
                f"Deployment failed: {error} "
                "Previous configuration restored and verified."
            )

        # Defensive fallback if rollback verification fails.
        candidate["status"] = "ROLLBACK_FAILED"

        return False, (
            f"Deployment failed: {error} "
            "WARNING: rollback verification failed."
        )


if __name__ == "__main__":
    candidate = {
        "router": "R1",
        "before": copy.deepcopy(routers["R1"]),
        "proposed": copy.deepcopy(routers["R1"]),
        "status": "APPROVED",
        "reviewer": "mentor",
        "reviewed_at": "demo-approval",
    }

    candidate["proposed"]["interfaces"]["eth0"] = "10.0.12.10/24"

    original_config = copy.deepcopy(routers["R1"])

    print("Original configuration:", original_config)

    success, message = deploy_candidate(
        candidate,
        simulate_failure=True,
    )

    print("\nResult:", message)
    print("Deployment successful:", success)
    print("Candidate status:", candidate["status"])
    print("Configuration after deployment attempt:", routers["R1"])
    print("Rollback verified:", routers["R1"] == original_config)