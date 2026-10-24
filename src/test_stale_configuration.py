import copy
import unittest

from unittest.mock import patch

from deployment import deploy_candidate
from routers import routers


class TestStaleConfiguration(unittest.TestCase):

    def test_stale_candidate_is_blocked(self):
        router_name = "R1"

        original_config = copy.deepcopy(routers[router_name])

        candidate = {
            "router": router_name,
            "before": copy.deepcopy(original_config),
            "proposed": copy.deepcopy(original_config),
            "status": "APPROVED",
            "reviewer": "demo-reviewer",
            "reviewed_at": "demo-approval",
        }

        candidate["proposed"]["interfaces"]["eth0"] = "10.0.12.10/24"

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