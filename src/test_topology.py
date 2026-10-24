
import copy

from routers import routers
from topology_validator import validate_topology


# Create a separate test network so the original stays unchanged.
test_network = copy.deepcopy(routers)

# Configure a loop for the same destination network.
destination = "192.168.30.0/24"

test_network["R1"]["routes"].append({
    "destination": destination,
    "next_hop": "10.0.12.2"
})

test_network["R2"]["routes"].append({
    "destination": destination,
    "next_hop": "10.0.23.3"
})

test_network["R3"]["routes"].append({
    "destination": destination,
    "next_hop": "10.0.12.1"
})

valid, message = validate_topology(test_network)

print("Routing loop test:", message)
print("Candidate should be rejected:", not valid)

print("\nOriginal network remains unchanged:")
print(routers)
