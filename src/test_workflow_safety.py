import copy
import unittest
from unittest.mock import patch

from routers import routers
from intents import validate_intent
from candidate_generator import generate_candidate
from approval import review_candidate, can_deploy
from deployment import deploy_candidate


class TestWorkflowSafety(unittest.TestCase):

    def test_unsupported_intent_rejected(self):
        intent = {
            "type": "delete_router",
            "router": "R1"
        }

        valid, message = validate_intent(intent)
        self.assertFalse(valid)

    def test_invalid_static_route_rejected(self):
        intent = {
            "type": "add_static_route",
            "router": "R1",
            "destination": "invalid-network",
            "next_hop": "10.0.12.2"
        }

        with patch("candidate_generator.routers", copy.deepcopy(routers)):
            candidate, message = generate_candidate(intent)

        self.assertIsNone(candidate)

    def test_conflicting_static_route_rejected(self):
        test_network = copy.deepcopy(routers)

        test_network["R1"]["routes"].append({
            "destination": "192.168.30.0/24",
            "next_hop": "10.0.12.2"
        })

        intent = {
            "type": "add_static_route",
            "router": "R1",
            "destination": "192.168.30.0/24",
            "next_hop": "10.0.12.2"
        }

        with patch("candidate_generator.routers", test_network):
            candidate, message = generate_candidate(intent)

        self.assertIsNone(candidate)

    def test_rejected_approval_blocks_deployment(self):
        candidate = {
            "router": "R1",
            "before": {
                "interfaces": {"eth0": "10.0.12.1/24"},
                "routes": []
            },
            "proposed": {
                "interfaces": {"eth0": "10.0.12.10/24"},
                "routes": []
            },
            "status": "PENDING_REVIEW"
        }

        success, message = review_candidate(
            candidate, "reject", "test-reviewer"
        )

        self.assertTrue(success)
        self.assertIn("REJECTED", message)
        self.assertEqual(candidate["status"], "REJECTED")
        self.assertFalse(can_deploy(candidate))

    def test_missing_approval_blocks_deployment(self):
        candidate = {
            "router": "R1",
            "before": {
                "interfaces": {"eth0": "10.0.12.1/24"},
                "routes": []
            },
            "proposed": {
                "interfaces": {"eth0": "10.0.12.10/24"},
                "routes": []
            },
            "status": "PENDING_REVIEW"
        }

        self.assertFalse(can_deploy(candidate))

    def test_failed_deployment_rolls_back(self):
        test_network = copy.deepcopy(routers)
        original_r1 = copy.deepcopy(test_network["R1"])

        candidate = {
            "router": "R1",
            "before": copy.deepcopy(test_network["R1"]),
            "proposed": {
                "interfaces": {"eth0": "10.0.12.10/24"},
                "routes": []
            },
            "status": "PENDING_REVIEW"
        }

        review_candidate(candidate, "approve", "test-reviewer")

        with patch("deployment.routers", test_network):
            result, message = deploy_candidate(
                candidate, simulate_failure=True
            )

        self.assertEqual(test_network["R1"], original_r1)
        self.assertEqual(candidate["status"], "ROLLED_BACK")


if __name__ == "__main__":
    unittest.main()
