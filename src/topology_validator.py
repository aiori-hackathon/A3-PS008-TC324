
from routers import routers


def detect_routing_loop(graph):
    """Detect a cycle in a directed router graph."""

    visited = set()
    active_path = set()

    def visit(router):
        if router in active_path:
            return True

        if router in visited:
            return False

        visited.add(router)
        active_path.add(router)

        for neighbor in graph.get(router, []):
            if visit(neighbor):
                return True

        active_path.remove(router)
        return False

    for router in graph:
        if visit(router):
            return True

    return False


def build_routing_graph(configurations=None):
    """Build a graph from router static routes and next-hop IPs."""

    if configurations is None:
        configurations = routers

    graph = {name: [] for name in configurations}
    ip_to_router = {}

    # Map each interface IP to its router.
    for router_name, data in configurations.items():
        for address in data["interfaces"].values():
            ip = address.split("/")[0]
            ip_to_router[ip] = router_name

    # Create edges from routers to their next-hop routers.
    for router_name, data in configurations.items():
        for route in data["routes"]:
            next_router = ip_to_router.get(route["next_hop"])

            if next_router is not None:
                graph[router_name].append(next_router)

    return graph


def validate_topology(configurations):
    """Reject a configuration graph that contains a cycle."""

    graph = build_routing_graph(configurations)

    if detect_routing_loop(graph):
        return False, f"Routing loop detected in graph: {graph}"

    return True, f"No cycle detected in graph: {graph}"


if __name__ == "__main__":
    example_graph = {
        "R1": ["R2"],
        "R2": ["R3"],
        "R3": ["R1"],
    }

    print("Example loop detected:", detect_routing_loop(example_graph))

    valid, message = validate_topology(routers)
    print("Current topology:", message)
