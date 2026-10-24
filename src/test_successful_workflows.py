import copy
import unittest

from unittest.mock import patch

from main import run_workflow
from routers import routers


class TestSuccessfulWorkflows(unittest.TestCase):

    def setUp(self):
        self.original_routers = copy.deepcopy(routers)

    def tearDown(self):
        routers.clear()
        routers.update(copy.deepcopy(self.original_routers))

    def test_interface_ip_change_success(self):
        intent = {
            "type": "change_interface_ip",
            "router": "R1",
            "interface": "eth0",
            "new_ip": "10.0.12.10/24",
        }

        candidate, message = run_workflow(
            intent=intent,
            decision="approve",
            simulate_failure=False,
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["status"], "DEPLOYED")
        self.assertEqual(
            routers["R1"]["interfaces"]["eth0"],
            "10.0.12.10/24",
        )

    def test_static_route_addition_success(self):
        intent = {
            "type": "add_static_route",
            "router": "R1",
            "destination": "192.168.30.0/24",
            "next_hop": "10.0.12.2",
        }

        candidate, message = run_workflow(
            intent=intent,
            decision="approve",
            simulate_failure=False,
        )

        self.assertIsNotNone(candidate)
        self.assertEqual(candidate["status"], "DEPLOYED")
        self.assertIn(
            {
                "destination": "192.168.30.0/24",
                "next_hop": "10.0.12.2",
            },
            routers["R1"]["routes"],
        )


if __name__ == "__main__":
    unittest.main()