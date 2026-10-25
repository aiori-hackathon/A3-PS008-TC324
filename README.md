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

Interface configuration changes are checked for valid router and interface references, valid IP addressing, and duplicate IP conflicts covered by the implementation.

### 6.3 Static Route Validation

Static route validation checks destination and next-hop syntax, duplicate destinations, and next-hop reachability on directly connected networks.

### 6.4 Routing-Loop Detection

The topology validator constructs a graph based on the implemented router and route relationships and uses cycle detection to identify potential routing-loop risks.

This is a simplified topology model rather than a complete destination-aware forwarding simulator.

### 6.5 Human Approval Gate

Candidate configurations require an approval decision before deployment.

Rejected or unapproved candidates cannot proceed through the normal deployment workflow.

### 6.6 Candidate Integrity Check

The approval module calculates a SHA-256 fingerprint from the candidate's router, original configuration, and proposed configuration.

During deployment, the system compares the current fingerprint with the stored fingerprint to detect candidate modifications made after approval.

This is an integrity consistency check. It does not provide a cryptographic signature or protect against an attacker who can modify both the candidate and its stored fingerprint.

### 6.7 Stale Configuration Protection

The deployment process checks whether the router's current configuration matches the original configuration recorded in the candidate.

If the configuration has changed since candidate generation, deployment is blocked to avoid applying a proposal based on outdated state.

### 6.8 Deployment Verification and Rollback

The deployment module supports successful deployment and simulated failure scenarios.

If verification fails, the system attempts to restore the previous configuration and verifies the restoration.

### 6.9 Audit Logging

The application records relevant workflow events, including intent validation, candidate generation, approval decisions, deployment outcomes, and rollback results.

Audit records are stored locally in a JSON file.

## 7. Simulated Router Testbed

The prototype uses three simulated routers.

| Router | Interface | Initial IP Address |
|---|---|---|
| R1 | eth0 | 10.0.12.1/24 |
| R2 | eth0 | 10.0.12.2/24 |
| R2 | eth1 | 10.0.23.2/24 |
| R3 | eth0 | 10.0.23.3/24 |

The router configurations are maintained in memory.

The testbed is used to demonstrate configuration validation, candidate generation, human approval, deployment verification, and rollback behavior.

The prototype does not directly configure physical routers.

## 8. Running the Project

### Prerequisites

- Python 3.10 or later is recommended.
- Git, if you want to clone the repository.
- Visual Studio Code or another Python-compatible editor is optional.

### Step 1: Clone the Repository

```bash
git clone https://github.com/aiori-hackathon/A3-PS008-TC324.git
```

### Step 2: Open the Project Directory

```bash
cd A3-PS008-TC324
```

### Step 3: Run the Demonstration

On Windows PowerShell, execute:

```powershell
python .\src\main.py
```

The demonstration runs two scenarios.

**Demo 1 — Successful Deployment**

- The intent is validated.
- A candidate configuration is generated.
- The reviewer approves the candidate.
- The deployment succeeds.
- The status becomes `DEPLOYED`.
- R1's interface IP changes from `10.0.12.1/24` to `10.0.12.10/24`.

**Demo 2 — Deployment Failure and Rollback**

- A second candidate proposes changing R1's IP to `10.0.12.20/24`.
- The reviewer approves the candidate.
- Simulated deployment verification fails.
- The previous configuration is restored and verified.
- The status becomes `ROLLED_BACK`.
- R1 retains the IP address `10.0.12.10/24`, which was its configuration before the second deployment attempt.

These demonstrations simulate deployment behavior using in-memory configurations. They do not modify physical routers.

## 9. Running Automated Tests

The project includes automated tests for configuration validation, candidate generation, approval, topology checks, deployment safety, and rollback.

From the project root, execute:

```powershell
python -m unittest discover -s src -p "test_*.py" -v
```

### Test Results

The current test suite contains **20 automated tests**.

The suite has been executed successfully during development, with all 20 tests passing.

The tests cover areas including:

- Valid and invalid interface IP changes.
- Invalid router and interface references.
- Static route validation.
- Routing-cycle detection.
- Candidate generation and workflow safety.
- Human approval and rejection.
- Candidate modification after approval.
- Stale configuration detection.
- Successful interface and static route workflows.
- Simulated deployment failure and rollback.

Run the test command again after modifying the code to verify the current state.

## 10. Project Structure

```text
A3-PS008-TC324/
│
├── README.md
│
└── src/
    ├── main.py
    ├── routers.py
    ├── intents.py
    ├── validator.py
    ├── route_validator.py
    ├── topology_validator.py
    ├── candidate_generator.py
    ├── approval.py
    ├── deployment.py
    ├── audit_log.py
    │
    ├── test_validator.py
    ├── test_candidate_loop.py
    ├── test_workflow_safety.py
    ├── test_approval_workflow.py
    ├── test_stale_configuration.py
    ├── test_successful_workflows.py
    ├── test_topology.py
    └── test_topology_safety.py
```

The structure above lists the main application and test modules. Additional repository files may be present.

## 11. Implementation Limitations

The current implementation is a prototype intended to demonstrate a reviewed configuration change workflow.

Its limitations include:

- Router configurations are maintained in memory and reset when the program starts.
- Deployment is simulated; the prototype does not configure physical routers.
- The demonstration reviewer identity is hard-coded.
- The approval fingerprint detects changes when the stored fingerprint remains unchanged; it is not a digital signature.
- Routing-loop detection uses the implemented topology graph and does not represent a complete production routing simulator.
- Static route validation uses a simplified connected-network model.
- Audit records are stored locally in JSON and are not tamper-proof.
- The audit log is not designed as a production-grade immutable record system.
- The application does not provide a complete multi-vendor network management interface.

These limitations should be considered when interpreting the results and evaluating production suitability.

## 12. Future Improvements

Potential future enhancements include:

- Adding an authenticated human-review interface.
- Integrating with a network device simulator.
- Supporting secure configuration adapters for selected network platforms.
- Improving destination-aware forwarding analysis and routing-loop detection.
- Adding stronger candidate approval signatures and integrity protections.
- Improving audit-log durability and tamper detection.
- Expanding automated tests for additional routing and configuration edge cases.
- Developing a graphical interface for candidate review and deployment status.
- Adding structured deployment reports and configuration diffs.
- Improving persistent storage and recovery behavior.

## 13. Conclusion

The AIORI PS-008 Network Management Agent demonstrates a controlled approach to network configuration changes.

The prototype validates supported intents, generates candidate configurations, requires human approval, checks candidate integrity and configuration freshness, and simulates deployment verification and rollback.

The automated test suite provides evidence that the implemented safety behaviors work for the tested scenarios.

The project establishes a foundation for further development toward more comprehensive and realistic network configuration management.

---

**Project:** AIORI PS-008 — Network Management Agent for Reviewed Configuration Changes  
**Team:** Ultimateblueteam  
**Hackathon:** AIORI Hackathon 3
