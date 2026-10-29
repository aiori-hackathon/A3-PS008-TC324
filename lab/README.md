# Lab: Wazuh configuration-file monitoring (data privacy posture)

Wazuh-powered detection of unauthorized changes to a privacy-relevant configuration file, using File
Integrity Monitoring (FIM), centrally pushed agent configuration, and custom child rules tagged for GDPR.
This complements the reviewed-change workflow in `src/` by detecting changes made **outside** that workflow.

## What it does

| Piece | Where | Purpose |
|---|---|---|
| Managed config file | `/etc/ps008/privacy.conf` (agent VM) | Privacy settings to protect (`lab/config/privacy.conf`) |
| FIM settings | `lab/wazuh/agent.conf` | Pushed from the manager: real-time monitoring, diff reporting |
| Custom child rules | `lab/wazuh/local_rules_ps008_config.xml` | Rules 100110-100112, children of Wazuh rules 550 / 554 / 553 |
| Compliance tags | `gdpr_II_5.1.f`, `gdpr_IV_35.7.d` | Alerts appear in the dashboard's GDPR view |

| Rule | Level | Parent | Fires when |
|---|---|---|---|
| 100110 | 10 | 550 | `privacy.conf` is modified |
| 100111 | 8 | 554 | a file is added under `/etc/ps008/` |
| 100112 | 12 | 553 | a file is deleted under `/etc/ps008/` |

## Lab topology (VirtualBox, Adapter 1 = NAT, Adapter 2 = Host-only 192.168.56.0/24)

| VM | OS | IP | Role |
|---|---|---|---|
| wazuh-server | Ubuntu 22.04 Server | 192.168.56.10 | Wazuh 4.14.9 all-in-one (manager, indexer, dashboard) |
| router-vm | Ubuntu 22.04 Server | 192.168.56.20 | Wazuh agent (shown as `Wazuh-router`), holds the monitored config file |

Adjust the IPs if yours differ.

## Setup

1. Install Wazuh on wazuh-server: `curl -sO https://packages.wazuh.com/4.14/wazuh-install.sh && sudo bash ./wazuh-install.sh -a`
2. Deploy the agent on router-vm from the dashboard (Agents -> Deploy new agent, server address 192.168.56.10).
3. On router-vm: `sudo mkdir -p /etc/ps008` and copy in `lab/config/privacy.conf`.
4. On wazuh-server: copy `lab/wazuh/agent.conf` to `/var/ossec/etc/shared/default/agent.conf`, run
   `sudo /var/ossec/bin/verify-agent-conf`, then `sudo systemctl restart wazuh-agent` on router-vm.
5. On wazuh-server: append `lab/wazuh/local_rules_ps008_config.xml` to `/var/ossec/etc/rules/local_rules.xml`,
   run `sudo /var/ossec/bin/wazuh-analysisd -t`, then `sudo systemctl restart wazuh-manager`.

## Demo (on router-vm, wait ~2 minutes after the agent restart)

    sudo sed -i 's/mask_pii=true/mask_pii=false/' /etc/ps008/privacy.conf     # -> rule 100110
    echo "test=1" | sudo tee /etc/ps008/extra.conf; sleep 15                  # -> rule 100111
    sudo rm /etc/ps008/extra.conf                                             # -> rule 100112

In the dashboard (Threat Hunting -> Events) search: `rule.id:(100110 or 100111 or 100112)`

## Observed result

| Time (Oct 30, 2026) | Rule | Level | Description |
|---|---|---|---|
| 00:34:31 | 100110 | 10 | privacy configuration file MODIFIED |
| 00:39:48 | 100111 | 8 | new file added to the managed config directory |
| 00:40:03 | 100112 | 12 | managed configuration file DELETED |

Screenshots: see `lab/screenshots/`.

## Limitations

- Detection only: Wazuh reports changes, it does not approve, block or roll them back.
- The reviewed-change workflow in `src/` still operates on simulated routers; it is not yet linked to this file.
- Single lab environment; rules match the fixed path `/etc/ps008/`.
