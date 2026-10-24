
import copy
import unittest
from unittest.mock import patch

from routers import routers
from candidate_generator import generate_candidate


class TestCandidateLoop(unittest.TestCase):

    def test_loop_candidate_is_rejected(self):
        test_network = copy.deepcopy(routers)

        destination = "192.168.30.0/24"

        test_network["R2"]["routes"].append({
            "destination": destination,
            "next_hop": "10.0.23.3"
        })

        test_network["R3"]["routes"].append({
            "destination": destination,
            "next_hop": "10.0.12.1"
        })

        intent = {
            "type": "add_static_route",
            "router": "R1",
            "destination": destination,
            "next_hop": "10.0.12.2"
        }

        # Temporarily use the test network inside the generator.
        with patch("candidate_generator.routers", test_network):
            candidate, message = generate_candidate(intent)

        self.assertIsNone(candidate)
        self.assertIn("loop", message.lower())

        print("\nLoop-producing candidate rejected:", message)


if __name__ == "__main__":
    unittest.main()
