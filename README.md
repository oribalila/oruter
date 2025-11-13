# Oruter Project

**Oruter (Or's Router)** is a project I created that implements a **packet-level router** in Python.  
It operates directly over raw sockets to capture, process, and forward Ethernet, ARP, IPv4, and ICMP packets between two virtual networks simulated using **Docker**.
> [!WARNING]  
> This overrides Docker’s default networking mechanism!

The environment setup is fully automated with **Ansible** and easily managed through shell **aliases**.

---

## Project Overview

The router acts as a Layer-2/3 device, capable of:
- Capturing and parsing Ethernet frames
- Handling ARP requests and replies
- Forwarding IPv4 packets and generating ICMP responses
- Dynamically updating ARP and routing tables
- Routing packets between two Docker bridge networks (`c1_iface` <--> `c2_iface`)

All components are organized for modularity and reproducibility.

---

## Repository Structure

```
.
├── aliases-scripts/       # Shell scripts and aliases to start, stop, and connect to the lab's containers
├── ansible/               # Infrastructure automation (Docker install, privileges setup, teardown)
├── docker/                # Docker environment defining lab networks and containers
├── router/                # Core Python router implementation
├── system_tests/          # End-to-end connectivity tests
├── Jenkinsfile            # CI/CD pipeline configuration
└── README.md              # This file
```

---

## Quick Start

### 1. Prepare the Environment
Run the Ansible setup to install Docker and grant Python raw-socket privileges:
```bash
ansible-playbook -i ansible/inventory/hosts ansible/project/main.yml --tags init
```
See [ansible/README.md](ansible/README.md)
> [!WARNING]  
> The command above has prerequisites steps you should do. See [ansible/README.md](ansible/README.md)

### 2. Start the Lab Environment
Bring up the two-network Docker lab:
```bash
lab-up
```
See [aliases-scripts/README.md](aliases-scripts/README.md) and [docker/README.md](docker/README.md)
> [!WARNING]  
> The command above has prerequisites steps you should do. See [aliases-scripts/README.md](aliases-scripts/README.md)

### 3. Run the Router
```bash
python3 router/main.py
```
See [router/README.md](router/README.md)

### 4. Test Connectivity
```bash
bash system_tests/test_connectivity.sh
```

---

## Development Notes

- This is a monorepo project. Work with it accordingly
- Each protocol (Ethernet, ARP, IPv4, ICMP) is implemented in its own module under `router/`
- Future work may include NAT support, IPv6, and dynamic routing protocols
- Use `wireshark` for debugging
- The environment can be easily reset using:
  ```bash
  lab-down
  ```
> [!IMPORTANT]  
> This project still has many refactors to apply and features to implement. See the other READMEs for details.

> [!IMPORTANT]  
> When forking or extending this project, **approach it with a DevOps mindset**.

---

## Documentation References

For detailed usage and setup of each component:
- [aliases-scripts/README.md](aliases-scripts/README.md)
- [ansible/README.md](ansible/README.md)
- [docker/README.md](docker/README.md)
- [router/README.md](router/README.md)

---

## License
This project is for educational and research purposes.

