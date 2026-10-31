
import copy
import json
import os
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from audit_log import record_event
from approval import can_deploy

MANAGED_FILE = Path("/etc/ps008/managed/router-policy.json")


def apply_managed_policy(candidate, policy, simulate_failure=False):
    """Deploy a real policy file only for a valid approved candidate."""

    if not can_deploy(candidate):
        return False, "Deployment blocked: valid human approval required."

    if not isinstance(policy, dict):
        return False, "Deployment blocked: invalid policy."

    if candidate.get("router") != policy.get("router"):
        return False, "Deployment blocked: router mismatch."

    if not MANAGED_FILE.is_file():
        return False, "Deployment failed: managed policy file missing."

    previous_bytes = MANAGED_FILE.read_bytes()
    previous_policy = json.loads(previous_bytes)

    if not isinstance(previous_policy, dict):
        return False, "Deployment blocked: existing policy is invalid."

    # Block deployment if the on-disk policy changed after review.
    if candidate.get("before") != previous_policy:
        return False, (
            "Deployment blocked: stale configuration. "
            "Current policy differs from reviewed baseline."
        )

    # Prevent changes to the router's management network.
    if (
        policy.get("management_interface")
        != previous_policy.get("management_interface")
        or policy.get("management_ip")
        != previous_policy.get("management_ip")
    ):
        return False, "Deployment blocked: management network is protected."

    # Require the proposed policy to advance its version.
    if (
        not isinstance(policy.get("policy_version"), int)
        or isinstance(policy.get("policy_version"), bool)
        or policy["policy_version"] <= previous_policy.get("policy_version", 0)
    ):
        return False, "Deployment blocked: policy version must increase."

    # Require the policy to be the one reviewed with the candidate.
    if policy != candidate.get("proposed_policy"):
        return False, "Deployment blocked: policy differs from reviewed proposal."

    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%fZ")
    backup = MANAGED_FILE.with_name(
        f"router-policy.{timestamp}.json.bak"
    )

    temp_path = None

    try:
        # Exclusive creation avoids overwriting an earlier backup.
        with backup.open("xb") as backup_file:
            backup_file.write(previous_bytes)
            backup_file.flush()
            os.fsync(backup_file.fileno())

        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=MANAGED_FILE.parent,
            prefix=".ps008-policy-",
            suffix=".tmp",
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)
            json.dump(policy, temp, indent=4)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())

        os.replace(temp_path, MANAGED_FILE)
        temp_path = None

        if simulate_failure:
            raise RuntimeError("Simulated verification failure.")

        actual = json.loads(MANAGED_FILE.read_text(encoding="utf-8"))
        if actual != policy:
            raise RuntimeError("Policy verification failed.")

        # Deployment is verified. Audit errors must not cause rollback.
        try:
            record_event(
                event="REAL_POLICY_DEPLOYED",
                router=candidate["router"],
                reviewer=candidate["reviewer"],
                details={
                    "policy_version": policy["policy_version"],
                    "backup_path": str(backup),
                    "managed_file": str(MANAGED_FILE),
                },
            )
        except Exception as audit_error:
            return True, (
                "Policy deployed and verified, but audit logging failed: "
                f"{audit_error}; backup: {backup}"
            )

        return True, f"Policy deployed and verified; backup: {backup}"


    except Exception as error:
        # Restore previous contents and verify the restoration.
        try:
            MANAGED_FILE.write_bytes(previous_bytes)
            if MANAGED_FILE.read_bytes() == previous_bytes:
                return False, f"Deployment failed: {error}; rollback verified."
            return False, f"Deployment failed: {error}; ROLLBACK FAILED."
        except OSError as rollback_error:
            return False, (
                f"Deployment failed: {error}; "
                f"ROLLBACK FAILED: {rollback_error}"
            )

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)
