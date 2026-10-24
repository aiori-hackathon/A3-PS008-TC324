
import ipaddress

from routers import routers


def validate_static_route(router_name, destination, next_hop):
    """Perform basic validation of a proposed static route."""

    if router_name not in routers:
        return False, f"Unknown router: {router_name}"

    try:
        network = ipaddress.ip_network(destination, strict=False)
        next_hop_ip = ipaddress.ip_address(next_hop)
    except ValueError:
        return False, "Invalid destination network or next-hop IP."

    router = routers[router_name]

    # Reject an existing route to the same destination.
    for route in router["routes"]:
        if route["destination"] == str(network):
            return False, "Conflicting route: destination already exists."

    # The next hop must be on a directly connected network.
    connected_networks = []

    for address in router["interfaces"].values():
        interface = ipaddress.ip_interface(address)
        connected_networks.append(interface.network)

    if not any(
        next_hop_ip in connected_network
        for connected_network in connected_networks
    ):
        return False, "Next hop is not on a directly connected network."

    return True, "Static route passed basic validation."


if __name__ == "__main__":
    tests = [
        ("R1", "192.168.30.0/24", "10.0.12.2"),
        ("R1", "invalid-network", "10.0.12.2"),
        ("R1", "192.168.40.0/24", "172.16.0.1"),
    ]

    for router, destination, next_hop in tests:
        valid, message = validate_static_route(
            router, destination, next_hop
        )
        print(
            f"{'VALID' if valid else 'REJECTED'}: "
            f"{destination} via {next_hop} — {message}"
        )
