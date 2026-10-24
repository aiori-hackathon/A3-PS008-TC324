
import unittest

from validator import validate_interface_change


class TestConfigurationValidator(unittest.TestCase):

    def test_valid_ip_change(self):
        valid, message = validate_interface_change(
            "R1", "eth0", "10.0.12.10/24"
        )
        self.assertTrue(valid)

    def test_invalid_ip_address(self):
        valid, message = validate_interface_change(
            "R1", "eth0", "999.1.1.1/24"
        )
        self.assertFalse(valid)

    def test_unknown_router(self):
        valid, message = validate_interface_change(
            "R9", "eth0", "10.0.12.10/24"
        )
        self.assertFalse(valid)

    def test_unknown_interface(self):
        valid, message = validate_interface_change(
            "R1", "eth9", "10.0.12.10/24"
        )
        self.assertFalse(valid)

    def test_duplicate_ip_address(self):
        valid, message = validate_interface_change(
            "R1", "eth0", "10.0.12.2/24"
        )
        self.assertFalse(valid)


if __name__ == "__main__":
    unittest.main(verbosity=2)
