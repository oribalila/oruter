# Aliases Scripts — Local Lab Shortcuts

This directory contains helper scripts and aliases for managing the local router lab environment.  
They simplify starting, stopping, and connecting to lab containers while handling host network configuration.

---

# Usage

## 1. Source env.sh
Source the environment file so the aliases are loaded into your current shell:
```bash
source aliases-scripts/env.sh
```

After sourcing, you’ll have access to these commands:
- `lab-up` — starts the lab environment
- `lab-down` — stops and cleans up the lab
- `lab-connect` — attaches to a running container shell

---

# Examples
```bash
source aliases-scripts/env.sh     # Load aliases
lab-up                            # Start the lab
lab-connect docker-client1-1      # Connect to a lab container
lab-down                          # Stop and clean up
```

---

# Notes
- You can add `source /path/to/aliases-scripts/env.sh` to your shell profile (e.g., `.bashrc` or `.zshrc`) to make aliases persistent
- Ensure `up.sh` and `down.sh` are executable (`chmod +x`)
- The `lab-connect` command opens a shell (`sh`) inside a container. If your container uses a different shell, modify `router_connect.sh` accordingly

