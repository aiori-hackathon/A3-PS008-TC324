
import copy

from routers import routers
from intents import validate_intent
from validator import validate_interface_change
from route_validator import validate_static_route
from topology_validator import validate_topology


def generate_candidate(intent):
    """Generate a proposed configuration without changing the original network."""

    # Step 1: Validate the structure of the intent.
    valid, message = validate_intent(intent)

    if not valid:
        return None, message

    router_name = intent["router"]

    # Step 2: Check whether the requested router exists.
    if router_name not in routers:
        return None, f"Unknown router: {router_name}"

    # Step 3: Create copies so the original configuration remains unchanged.
    current_config = copy.deepcopy(routers[router_name])
    candidate_config = copy.deepcopy(current_config)

    # Step 4: Handle interface IP changes.
    if intent["type"] == "change_interface_ip":
        interface = intent["interface"]
        new_ip = intent["new_ip"]

        valid, message = validate_interface_change(
            router_name, interface, new_ip
        )

        if not valid:
            return None, message

        candidate_config["interfaces"][interface] = new_ip

    # Step 5: Handle static route additions.
    elif intent["type"] == "add_static_route":
        destination = intent["destination"]
        next_hop = intent["next_hop"]

        # Validate the route before creating the candidate.
        valid, message = validate_static_route(
            router_name, destination, next_hop
        )

        if not valid:
            return None, message

        route = {
            "destination": destination,
            "next_hop": next_hop,
        }

        # Prevent adding an identical route.
        if route in candidate_config["routes"]:
            return None, "This route already exists."

        candidate_config["routes"].append(route)

    
    # Check the complete proposed network before review.
    proposed_network = copy.deepcopy(routers)
    proposed_network[router_name] = candidate_config

    valid, message = validate_topology(proposed_network)

    if not valid:
        return None, message

    candidate = {
        "router": router_name,
        "before": current_config,
        "proposed": candidate_config,
        "status": "PENDING_REVIEW",
    }


    return candidate, "Candidate generated. Human review is required."


if __name__ == "__main__":
    example_intent = {
    "type": "add_static_route",
    "router": "R1",
    "destination": "192.168.30.0/24",
    "next_hop": "10.0.12.2",
}

    candidate, message = generate_candidate(example_intent)

    print(message)

    if candidate:
        print("\nRouter:", candidate["router"])
        print("Status:", candidate["status"])

        print("\nBEFORE:")
        print(candidate["before"])

        print("\nPROPOSED:")
        print(candidate["proposed"])

        print("\nOriginal network remains unchanged:")
        print(routers["R1"])
