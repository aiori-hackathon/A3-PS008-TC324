import unittest
from unittest.mock import patch

from main import run_workflow
from routers import routers


class TestApprovalWorkflow(unittest.TestCase):

    def test_rejected_candidate_is_not_deployed(self):
        intent = {
            "type": "change_interface_ip",
            "router": "R1",
            "interface": "eth0",
            "new_ip": "10.0.12.10/24",
        }

        original_config = {
            router: {
                "interfaces": config["interfaces"].copy(),
                "routes": config["routes"].copy(),
            }
            for router, config in routers.items()
        }

        with patch("main.deploy_candidate") as mock_deploy:
            candidate, message = run_workflow(
                intent=intent,
                decision="reject",
                simulate_failure=False,
            )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["status"], "REJECTED")
        mock_deploy.assert_not_called()
        self.assertEqual(routers, original_config)


if __name__ == "__main__":
    unittest.main()
