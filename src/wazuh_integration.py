import json
import os
import tempfile
from pathlib import Path
from datetime import datetime, timezone

from audit_log import record_event

CONFIG_DIR = Path("/etc/ps008/agent-output")
CONFIG_FILE = CONFIG_DIR / "approved-change.json"


def deploy_approved_config(change_id, reviewer, config, approved=False):
    """Deploy a reviewed configuration artifact for Wazuh monitoring."""

    if approved is not True:
        raise PermissionError("Deployment requires explicit approval.")

    if not change_id or not reviewer:
        raise ValueError("Change ID and reviewer are required.")

    if not isinstance(config, dict):
        raise ValueError("Configuration must be a dictionary.")

    payload = {
        "change_id": change_id,
        "reviewer": reviewer,
        "approved": True,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "configuration": config,
    }

    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8",
            dir=CONFIG_DIR,
            prefix=".ps008-",
            suffix=".tmp",
            delete=False,
        ) as temp:
            temp_path = Path(temp.name)
            json.dump(payload, temp, indent=4)
            temp.write("\n")
            temp.flush()
            os.fsync(temp.fileno())

        os.replace(temp_path, CONFIG_FILE)

    finally:
        if temp_path is not None:
            temp_path.unlink(missing_ok=True)

    record_event(
        event="APPROVED_CONFIG_ARTIFACT_WRITTEN",
        router="R1",
        reviewer=reviewer,
        details={
            "change_id": change_id,
            "path": str(CONFIG_FILE),
        },
    )

    return payload
