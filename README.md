# AIORI-3-HACKATHON-PROJECTS
This repository will contain the code and resources for the AIORI-3 hackathon that will be developed during the AIORI-3
## Team Introduction Video

**AIORI Hackathon 3 — Ultimateblueteam**
Problem Statement: PS008 — Network Management Agent for Reviewed Configuration Changes
YouTube Link: https://youtube.com/shorts/BY337KfnYno?feature=share
# AIORI PS008 — Network Management Agent for Reviewed Configuration Changes

## 1. Project Overview

The Network Management Agent is a prototype designed to validate proposed network configuration changes, generate candidate configurations, request human approval, and simulate safe deployment.

The system includes configuration validation, routing-loop detection, approval checks, rollback handling, and audit logging.

## 2. Objectives

- Accept supported network configuration intents.
- Validate proposed changes before deployment.
- Generate candidate configurations for review.
- Require human approval before deployment.
- Detect routing-loop risks using the implemented topology validator.
- Restore the previous configuration when simulated deployment verification fails.
- Record workflow events in an audit log.

## 3. Supported Configuration Intents

### Change Interface IP

Changes the IP address assigned to a supported router interface.

Example:

```json
{
  "type": "change_interface_ip",
  "router": "R1",
  "interface": "eth0",
  "new_ip": "10.0.12.10/24"
}
```

### Add Static Route

Adds a static route to a router's configuration.

Example:

```json
{
  "type": "add_static_route",
  "router": "R1",
  "destination": "192.168.30.0/24",
  "next_hop": "10.0.12.2"
}
```

## 4. System Workflow

1. Validate the requested intent.
2. Generate a candidate configuration.
3. Validate the proposed configuration and topology.
4. Present the candidate for human review.
5. Stop if approval is not granted.
6. Simulate deployment of an approved candidate.
7. Verify the resulting configuration.
8. Restore the previous configuration if simulated verification fails.
9. Record relevant events in the audit log.

## 5. Safety Features

- Intent validation.
- Interface and IP validation.
- Static route validation.
- Routing-loop checks.
- Human approval gate.
- Stale-configuration protection.
- Deployment verification.
- Automatic rollback in the simulation.
- JSON-based audit logging.

## 6. Project Structure

The `src` directory contains the application modules, router configuration, validators, approval and deployment logic, audit logging, and automated tests.

## 7. Running the Project

Run the demonstration from the project root:

```powershell
python .\src\main.py
```

The current demonstration approves a candidate and simulates deployment verification failure to demonstrate rollback.

## 8. Running Tests

Run the test suite:

```powershell
python -m unittest discover -s src -p "test_*.py" -v
```

The current test suite has passed 19 tests in the development environment.

Run the command again after any code changes to confirm the current result.

## 9. Implementation Limitations

- Router configurations are maintained in memory.
- Deployment is simulated; the prototype does not configure physical routers.
- The demonstration reviewer is hard-coded.
- Routing-loop detection is based on the implemented topology model and does not represent a complete production routing simulator.
- Audit records are stored locally in a JSON file.

## 10. Future Improvements

- Add an authenticated human-review interface.
- Integrate with a network device simulator.
- Improve routing analysis with destination-aware forwarding checks.
- Add stronger audit-log integrity protections.
- Expand automated tests for additional invalid and conflicting configurations.
- Develop a demonstration interface for reviewers.