import copy
import unittest
from unittest.mock import patch

from routers import routers
from approval import review_candidate
from deployment import deploy_candidate


class TestStaleConfiguration(unittest.TestCase):

    def test_stale_candidate_is_blocked(self):
        router_name = "R1"
        original_config = copy.deepcopy(routers[router_name])

        candidate = {
            "router": router_name,
            "before": copy.deepcopy(original_config),
            "proposed": copy.deepcopy(original_config),
            "status": "PENDING_REVIEW",
        }

        candidate["proposed"]["interfaces"]["eth0"] = "10.0.12.10/24"

        # Approve the candidate using the real approval workflow.
        success, message = review_candidate(
            candidate,
            decision="approve",
            reviewer="demo-reviewer",
        )

        self.assertTrue(success, message)
        self.assertEqual(candidate["status"], "APPROVED")

        try:
            # Simulate another process changing R1 after approval.
            with patch.dict(
                routers,
                {
                    router_name: {
                        "interfaces": {"eth0": "10.0.12.99/24"},
                        "routes": [],
                    }
                },
            ):
                success, message = deploy_candidate(candidate)

                self.assertFalse(success)
                self.assertIn("configuration has changed", message)
                self.assertEqual(candidate["status"], "APPROVED")

        finally:
            # Restore the original configuration after the test.
            routers[router_name] = original_config


if __name__ == "__main__":
    unittest.main()