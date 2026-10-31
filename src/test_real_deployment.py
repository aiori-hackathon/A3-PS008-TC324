
import copy
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import real_deployment
from approval import review_candidate


class TestRealDeployment(unittest.TestCase):

    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp_dir.cleanup)

        self.policy_file = (
            Path(self.temp_dir.name) / "router-policy.json"
        )

        self.current = {
            "router": "R1",
            "management_interface": "enp0s8",
            "management_ip": "192.168.56.5/24",
            "policy_version": 4,
            "description": "Current policy",
        }

        self.policy_file.write_text(
            json.dumps(self.current),
            encoding="utf-8",
        )

        self.file_patch = patch.object(
            real_deployment, "MANAGED_FILE", self.policy_file
        )
        self.file_patch.start()
        self.addCleanup(self.file_patch.stop)

        self.audit_patch = patch.object(
            real_deployment, "record_event"
        )
        self.mock_audit = self.audit_patch.start()
        self.addCleanup(self.audit_patch.stop)

    def make_candidate(self, before=None, proposed=None):
        if before is None:
            before = copy.deepcopy(self.current)

        if proposed is None:
            proposed = copy.deepcopy(self.current)
            proposed["policy_version"] += 1

        candidate = {
            "router": "R1",
            "before": before,
            "proposed": proposed,
            "proposed_policy": copy.deepcopy(proposed),
            "status": "PENDING_REVIEW",
        }

        return candidate, proposed

    def approve(self, candidate):
        approved, message = review_candidate(
            candidate,
            decision="approve",
            reviewer="test-reviewer",
        )
        self.assertTrue(approved, message)

    def test_unapproved_deployment_blocked(self):
        candidate, proposed = self.make_candidate()

        success, message = real_deployment.apply_managed_policy(
            candidate, proposed
        )

        self.assertFalse(success)
        self.assertIn("approval", message.lower())
        self.assertEqual(
            json.loads(self.policy_file.read_text()),
            self.current,
        )

    def test_stale_configuration_blocked(self):
        stale = copy.deepcopy(self.current)
        stale["policy_version"] = 2

        candidate, proposed = self.make_candidate(before=stale)
        self.approve(candidate)

        success, message = real_deployment.apply_managed_policy(
            candidate, proposed
        )

        self.assertFalse(success)
        self.assertIn("stale", message.lower())

    def test_management_network_protected(self):
        candidate, proposed = self.make_candidate()
        proposed["management_ip"] = "192.168.56.99/24"
        candidate["proposed"] = copy.deepcopy(proposed)
        candidate["proposed_policy"] = copy.deepcopy(proposed)

        self.approve(candidate)

        success, message = real_deployment.apply_managed_policy(
            candidate, proposed
        )

        self.assertFalse(success)
        self.assertIn("management network", message.lower())

    def test_simulated_failure_rolls_back(self):
        candidate, proposed = self.make_candidate()
        self.approve(candidate)

        original_bytes = self.policy_file.read_bytes()

        success, message = real_deployment.apply_managed_policy(
            candidate,
            proposed,
            simulate_failure=True,
        )

        self.assertFalse(success)
        self.assertIn("rollback verified", message.lower())
        self.assertEqual(
            self.policy_file.read_bytes(),
            original_bytes,
        )

    def test_successful_deployment_audited(self):
        candidate, proposed = self.make_candidate()
        self.approve(candidate)

        success, message = real_deployment.apply_managed_policy(
            candidate, proposed
        )

        self.assertTrue(success, message)
        self.assertEqual(
            json.loads(self.policy_file.read_text()),
            proposed,
        )
        self.mock_audit.assert_called_once()

        kwargs = self.mock_audit.call_args.kwargs
        self.assertEqual(kwargs["event"], "REAL_POLICY_DEPLOYED")
        self.assertEqual(kwargs["details"]["policy_version"], 5)
    def test_audit_failure_does_not_rollback(self):
        candidate, proposed = self.make_candidate()
        self.approve(candidate)

        self.mock_audit.side_effect = OSError("Audit disk unavailable")

        success, message = real_deployment.apply_managed_policy(
            candidate, proposed
        )

        self.assertTrue(success)
        self.assertIn("audit logging failed", message.lower())
        self.assertEqual(
            json.loads(self.policy_file.read_text()),
            proposed,
        )
        self.mock_audit.assert_called_once()


if __name__ == "__main__":
    unittest.main()
