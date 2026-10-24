import copy
import unittest

from routers import routers
from topology_validator import validate_topology


class TestTopologySafety(unittest.TestCase):

    def setUp(self):
        self.network = copy.deepcopy(routers)

    def test_normal_topology_is_accepted(self):
        valid, message = validate_topology(self.network)

        self.assertTrue(valid, message)

    def test_directed_routing_loop_is_rejected(self):
        network = copy.deepcopy(self.network)

        network["R1"]["routes"] = [
            {
                "destination": "192.168.30.0/24",
                "next_hop": "10.0.12.2",
            }
        ]

        network["R2"]["routes"] = [
            {
                "destination": "192.168.30.0/24",
                "next_hop": "10.0.23.3",
            }
        ]

        network["R3"]["routes"] = [
            {
                "destination": "192.168.30.0/24",
                "next_hop": "10.0.23.2",
            }
        ]

        valid, message = validate_topology(network)

        self.assertFalse(valid)
        self.assertIn("Routing loop detected", message)

    def test_validation_does_not_modify_original_network(self):
        original = copy.deepcopy(self.network)

        validate_topology(self.network)

        self.assertEqual(self.network, original)


if __name__ == "__main__":
    unittest.main()
