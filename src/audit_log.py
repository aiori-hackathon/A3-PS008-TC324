import json
from datetime import datetime
from zoneinfo import ZoneInfo
from pathlib import Path

AUDIT_FILE = Path(__file__).resolve().parent / "audit_log.json"


def record_event(event, router=None, reviewer=None, details=None):
    """Record a configuration workflow event in the audit log."""

    entry = {
        "timestamp": datetime.now(ZoneInfo("Asia/Kolkata")).isoformat(),
        "event": event,
        "router": router,
        "reviewer": reviewer,
        "details": details or {}
    }

    records = []

    if AUDIT_FILE.exists():
        try:
            with AUDIT_FILE.open("r", encoding="utf-8") as file:
                records = json.load(file)

            if not isinstance(records, list):
                records = []

        except (json.JSONDecodeError, OSError):
            records = []

    records.append(entry)

    with AUDIT_FILE.open("w", encoding="utf-8") as file:
        json.dump(records, file, indent=4)

    return entry


def read_audit_log():
    """Return all recorded audit events."""

    if not AUDIT_FILE.exists():
        return []

    with AUDIT_FILE.open("r", encoding="utf-8") as file:
        return json.load(file)


if __name__ == "__main__":
    record_event(
        event="AUDIT_LOG_TEST",
        router="R1",
        reviewer="demo-reviewer",
        details={"message": "Audit logging is working."}
    )

    print(json.dumps(read_audit_log(), indent=4))
