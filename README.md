# AIORI PS-008 — Network Management Agent for Reviewed Configuration Changes

**AIORI Hackathon 3 — Ultimateblueteam**

**Problem Statement:** PS008 — Network Management Agent for Reviewed Configuration Changes

## Team Introduction Video

**YouTube Link:** https://youtube.com/shorts/BY337KfnYno?feature=share

---

## 1. Project Overview

The Network Management Agent is a prototype designed to validate proposed network configuration changes, generate candidate configurations, require human approval, and simulate safe deployment.

The system aims to reduce the risks associated with network configuration changes by validating proposed modifications before deployment and preventing unapproved changes from being applied.

The prototype includes interface IP validation, static route validation, routing-loop detection, candidate integrity checks, stale-configuration protection, deployment verification, rollback handling, and audit logging.

The project uses an in-memory router testbed to demonstrate the configuration management workflow without modifying physical network devices.

## 2. Objectives

The main objectives of this project are:

- Accept supported network configuration intents.
- Validate requested changes before generating a candidate configuration.
- Generate candidate configurations for human review.
- Require explicit approval before deployment.
- Detect invalid interface configurations and conflicting static routes.
- Identify potential routing-loop risks using the implemented topology validator.
- Detect modifications to a candidate after approval when its stored fingerprint remains unchanged.
- Prevent deployment when the original router configuration has changed since the candidate was generated.
- Verify the result of a simulated deployment.
- Restore the previous configuration when simulated deployment verification fails.
- Record important workflow events in a local JSON audit log.
- Test the implementation using an automated test suite.

## 3. Supported Configuration Intents

The prototype supports two configuration intent types.

### 3.1 Change Interface IP

This intent changes the IP address assigned to a supported router interface.

**Example:**

```json
{
  "type": "change_interface_ip",
  "router": "R1",
  "interface": "eth0",
  "new_ip": "10.0.12.10/24"
}
```

The system validates the intent, checks the target router and interface, validates the proposed IP address, and generates a candidate configuration for review.

The proposed configuration is not applied to the router state during candidate generation.

### 3.2 Add Static Route

This intent adds a static route to a supported router's configuration.

**Example:**

```json
{
  "type": "add_static_route",
  "router": "R1",
  "destination": "192.168.30.0/24",
  "next_hop": "10.0.12.2"
}
```

The route validator checks the route's address syntax, destination conflicts, and next-hop reachability using the implemented connected-network model.

A valid route is prepared as a candidate configuration for human review before deployment.

## 4. System Architecture

The application is organized into modules responsible for validation, candidate generation, approval, deployment, topology checks, and audit logging.

### Main Components

| Component | Responsibility |
|---|---|
| `routers.py` | Maintains the simulated router configurations |
| `intents.py` | Validates supported configuration intent structures and values |
| `validator.py` | Validates interface configuration changes |
| `route_validator.py` | Validates static route configurations |
| `topology_validator.py` | Detects cycles in the implemented router topology graph |
| `candidate_generator.py` | Creates and validates proposed configuration candidates |
| `approval.py` | Records human review decisions and checks candidate fingerprints |
| `deployment.py` | Simulates deployment, verifies outcomes, and handles rollback |
| `audit_log.py` | Records workflow events in a local JSON audit log |
| `main.py` | Coordinates the complete configuration management workflow |

Automated tests are included in the `src` directory.

## 5. System Workflow

The application follows a controlled configuration change workflow.

1. **Intent validation:** The requested configuration change is checked for valid structure and supported values.
2. **Candidate generation:** A proposed configuration is created without immediately modifying the router's current configuration.
3. **Configuration validation:** The proposed change is checked against the relevant interface, IP address, or static route rules.
4. **Topology validation:** The implemented topology validator checks for routing cycles.
5. **Human review:** A reviewer approves or rejects the candidate.
6. **Approval verification:** Deployment is blocked if the candidate is not approved or if its integrity check fails.
7. **Stale configuration check:** The deployment process checks whether the router configuration still matches the candidate's original configuration.
8. **Deployment:** An approved and valid candidate is applied to the simulated router configuration.
9. **Verification:** The deployment process checks the simulated deployment result.
10. **Rollback:** If simulated deployment verification fails, the previous configuration is restored and verified.
11. **Audit logging:** Relevant workflow events and outcomes are recorded in the local audit log.

## 6. Safety Features

### 6.1 Intent Validation

The system validates incoming configuration requests before processing them. Unsupported intent types and invalid input values are rejected.

### 6.2 Interface and IP Validation
