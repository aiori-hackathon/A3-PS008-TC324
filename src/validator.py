
import ipaddress

from routers import routers


def validate_interface_change(router_name, interface, new_ip):
    """Validate an IP address change on a known router interface."""

    # Check whether the router exists.
    if router_name not in routers:
        return False, f"Unknown router: {router_name}"

    # Check whether the interface exists.
    interfaces = routers[router_name]["interfaces"]

    if interface not in interfaces:
        return False, f"Unknown interface: {interface}"

    # Check whether the new IP address and prefix are valid.
    try:
        new_address = ipaddress.ip_interface(new_ip)
    except ValueError:
        return False, f"Invalid IP address or prefix: {new_ip}"

    # Prevent assigning the same IP address to two interfaces.
    for other_router, data in routers.items():
        for other_interface, address in data["interfaces"].items():

            # Ignore the interface being changed.
            if (other_router, other_interface) == (router_name, interface):
                continue

            existing_address = ipaddress.ip_interface(address)

            if new_address.ip == existing_address.ip:
                return False, (
                    f"IP address already used by "
                    f"{other_router} ({other_interface})"
                )

    return True, "Configuration passed basic validation."


if __name__ == "__main__":
    examples = [
        ("R1", "eth0", "10.0.12.10/24"),
        ("R1", "eth0", "999.1.1.1/24"),
        ("R9", "eth0", "10.0.12.10/24"),
        ("R1", "eth0", "10.0.12.2/24"),
    ]

    for router, interface, new_ip in examples:
        valid, message = validate_interface_change(
            router, interface, new_ip
        )

        print(f"\nChange: {router} {interface} -> {new_ip}")
        print(f"Result: {'VALID' if valid else 'REJECTED'}")
        print(f"Reason: {message}")
