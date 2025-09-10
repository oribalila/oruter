# Ansible — Router Infrastructure

This directory automates preparing, configuring, and tearing down the environment for the `Oruter` router.  
The inventory is already defined under `ansible/inventory`.  
The `init` role installs Docker and Docker Compose and grants Python raw-socket capabilities.  
The `tear` role removes raw-socket capabilities from Python (keeps Docker and Docker Compose installed).

---

# Installation & Setup

## 1. Install external roles (mandatory, before init)
```bash
ansible-galaxy install -r requirements.yml -p roles/
```

## 2. Create env.sh
Create `ansible/env.sh` with your credentials and interpreter path:
```bash
export ANSIBLE_USER="<YOUR-USERNAME>"
export ANSIBLE_PASS="<YOUR-PASSWORD>"
export ANSIBLE_BECOME_PASS="<YOUR-SUDO-PASSWORD>"
export PYTHON_PATH="<FULL-PATH-TO-YOUR-PYTHON-BINARY>"  # Use the real binary path, not a symlink
```
It is **excluded from the repository** via the `.gitignore` because it contains sensitive data.

## 3. Source env.sh
```bash
source ansible/env.sh
```

## 4. Run the init role to set up the router environment
```bash
ansible-playbook -i inventory/hosts project/main.yml --tags init
```

## 5. (Optional) Teardown
```bash
ansible-playbook -i inventory/hosts project/main.yml --tags tear
```

---

# Notes
- Grep for `lookup` to replace references to `env.sh` with hard-coded variables directly in the YAML files
- Ensure `PYTHON_PATH` matches the actual Python interpreter used by Ansible (for example `/usr/bin/python3.12`).  
  You can verify which binary is being used by running:
  ```bash
  file $(which python3) # Likely points to your desired Python binary
  ```
---

# Tips

**Dry run (check mode):**
```bash
ansible-playbook -i inventory/hosts project/main.yml --check
```

**Verbose output:**
```bash
ansible-playbook -vvv -i inventory/hosts project/main.yml
```

