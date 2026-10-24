
import ipaddress


SUPPORTED_INTENTS = {
    "change_interface_ip",
    "add_static_route",
}


def validate_intent(intent):
    """Check the structure and basic values of a network intent."""

    if not isinstance(intent, dict):
        return False, "Intent must be a dictionary."

    intent_type = intent.get("type")
    router = intent.get("router")

    if intent_type not in SUPPORTED_INTENTS:
        return False, "Unsupported intent type."

    if not isinstance(router, str) or not router:
        return False, "A router name is required."

    if intent_type == "change_interface_ip":
        interface = intent.get("interface")
        address = intent.get("new_ip")

        if not isinstance(interface, str) or not interface:
            return False, "An interface name is required."

        if not isinstance(address, str):
            return False, "A new IP address is required."

        try:
            ipaddress.ip_interface(address)
        except ValueError:
            return False, "Invalid IP address or prefix."

    elif intent_type == "add_static_route":
        destination = intent.get("destination")
        next_hop = intent.get("next_hop")

        if not isinstance(destination, str):
            return False, "A destination network is required."

        if not isinstance(next_hop, str):
            return False, "A next-hop IP address is required."

        try:
            ipaddress.ip_network(destination, strict=False)
        except ValueError:
            return False, "Invalid destination network."

        try:
            ipaddress.ip_address(next_hop)
        except ValueError:
            return False, "Invalid next-hop IP address."

    return True, "Intent structure and values are valid."


if __name__ == "__main__":
    examples = [
        {
            "type": "change_interface_ip",
            "router": "R1",
            "interface": "eth0",
            "new_ip": "10.0.12.10/24",
        },
        {
            "type": "add_static_route",
            "router": "R1",
            "destination": "192.168.30.0/24",
            "next_hop": "10.0.12.2",
        },
        {
            "type": "unknown_action",
            "router": "R1",
        },
    ]

    for intent in examples:
        valid, message = validate_intent(intent)
        print(f"\nIntent: {intent}")
        print(f"Result: {'VALID' if valid else 'REJECTED'}")
        print(f"Reason: {message}")
