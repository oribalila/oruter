# Docker Environment — Router Lab Topology

This directory defines the Docker environment used to emulate the router lab.  
It launches two lightweight client containers, each connected to a different bridge network that represents a separate LAN segment.  
These two networks simulate independent subnets that the router connects and routes between.

---

# Usage

## 1. Start the environment
Bring up the lab containers and networks:
```bash
docker compose up -d
```

## 2. Stop and remove the environment
Tear down the lab when done:
```bash
docker compose down
```

---

# How It Works
The Docker Compose configuration creates:
- Two client containers (`client1` and `client2`)
- Two bridge networks (`c1_network` and `c2_network`)
- Distinct subnets (e.g., `1.1.1.0/24` and `2.2.2.0/24`)
- Custom bridge names (`c1_iface`, `c2_iface`) so the router knows which interfaces to listen on

This setup simulates two independent LANs connected through the router for functional and connectivity testing.

---

# Customization

## Change the client image
Modify the `.env` file to use a different base image:
```bash
CLIENT_IMAGE=<your-image>
```
## Adding More Containers

To attach additional containers to an existing network, extend `docker-compose.yml` with another service definition.  
For example, to add a debugging client to `c1_network`:

```yaml
  debug_client:
    image: alpine:3.15
    tty: true
    networks:
      c1_network:
```

After saving the file, rebuild the environment:
```bash
docker compose up -d
```

The new container will appear on the same subnet and will be able to communicate with other containers on that network.  
When the router is started, it will also have connectivity to containers in the second network.

## Adjust Network Settings

You can modify `docker-compose.yml` to change subnet ranges or bridge interface names if they conflict with your host configuration.  
If you make these changes, ensure the router configuration and any related scripts reference the updated values.

---

# Notes

- The router listens to both bridges and forwards packets between them
- The environment is minimal and designed for reproducible network simulations
- When altering interface or subnet names, remember to update the router configuration and any related scripts accordingly

---

