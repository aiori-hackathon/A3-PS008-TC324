
# Simulated three-router network for AIORI PS008

routers = {
    "R1": {
        "interfaces": {
            "eth0": "10.0.12.1/24"
        },
        "routes": []
    },
    "R2": {
        "interfaces": {
            "eth0": "10.0.12.2/24",
            "eth1": "10.0.23.2/24"
        },
        "routes": []
    },
    "R3": {
        "interfaces": {
            "eth0": "10.0.23.3/24"
        },
        "routes": []
    }
}


def display_routers():
    """Display the simulated routers and their interfaces."""
    for router_name, router_data in routers.items():
        print(f"\nRouter: {router_name}")

        for interface, ip_address in router_data["interfaces"].items():
            print(f"  {interface}: {ip_address}")

        print(f"  Routes: {router_data['routes']}")


if __name__ == "__main__":
    display_routers()
