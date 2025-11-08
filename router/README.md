# Router

**The heart of this repository!**  
This directory contains the core Python implementation of the router!  
It captures, processes, and forwards packets between two Docker bridge networks created by the lab environment.
> [!IMPORTANT]  
> It acts as **a combination of a Layer-2 switch and a Layer-3 router**: just how modern routers work.

---

## Running the Router

Make sure the environment is already set up (Ansible, Docker, and aliases steps completed).

Afterwards, run:
```bash
pip3 install -r requirements.txt # Run once
python3 main.py
```

The router requires **raw-socket** access, which is granted automatically by the Ansible `init` role.

Once running, it will:
- Listen on both bridge interfaces (`c1_iface` and `c2_iface`)
- Forward packets between them according to `routing_table.txt`
- Update the routing table dynamically based on received ARP packets
- Use the ARP table when resolving next-hop addresses
- Handle Ethernet, ARP, IPv4, and ICMP traffic

You can verify connectivity by running a ping from a client in one network to a client in another network:
```bash
docker exec -it docker-client1-1 ping 2.2.2.2
```

---

## How It Works

The router listens for incoming Ethernet frames (excluding the preamble and CRC) on its interfaces and handles them as needed (altering, routing, responding, etc.):  

Supported protocols and features are:
- **Ethernet** — parses and create frame headers and identifies upper-layer protocols
- **ARP** — responds to ARP requests and updates the arp and the routing table dynamically
> [!NOTE]  
> Initial routing decisions are based on `routing_table.txt`.
- **IPv4** — decrements TTL, recalculates checksums, fragment packets based on its MTU, and forwards packets based on destination routes
> [!NOTE]  
> The router forwards any IPv4 packet to its destination. It just can’t parse all of the packet’s upper-layer headers (as most routers can’t).
- **ICMP** — replies to echo requests

> [!IMPORTANT]  
> To support additional protocols, you can simply create a new protocol file (see `ipv4.py` as an example) that parses and handles the protocol, and then extend `packet.py` to integrate it.  
> This idea is quite ambitious — but with enough protocol support, the router could technically evolve into more than just a combination of a Layer-2 switch and a Layer-3 router (a modern router):  
> a hybrid between a traditional router and a protocol-aware proxy (somewhat like Burp Suite, but for the supported protocols).  
> Going in this direction would open the option to support Layer 4 and Layer 5 protocol parsing.

---

## Debugging

For debugging the router, what I’d recommend is to:
- Read through its logs
- Add additional logs and prints in the code
- Use `wireshark` on its interfaces and veths

---

## Future Improvements
#### Design Patterns:
- Refactor with a clear goal in mind: either prioritize *readability* (for easier future development) or *efficiency* (for a closer “how it really works” performance model)
> [!WARNING]  
> This project is already optimized within Python’s constraints.  
> The intention is *not* to pursue both readability *and* efficiency simultaneously.  
> Since true performance would require Go/C, decide whether the refactor should target  
> *cleaner, more maintainable Python* or *lower-level, performance-oriented Python*.
- Add more validation (perhaps refactor with `pydantic`); Good for readability, bad for performance.
- Avoid redundancy: `self.interfaces` and `self.myIp` are tightly coupled, etc.
#### UI\UX
- Add ability to interrupt the router
- Add ability to manually config the router from the terminal
- Better print the logs
- Visualize the logs in Grafana
#### Router Functionality
- Add NAT to connect to the internet
- Implement dynamic routing protocols (e.g., OSPF, EIGRP, BGP)
#### Protocol Support
- Add IPv6 support
- Expand ICMP error handling and logging mechanisms
- Support ICMP requests without timestamp
#### Crazy Ideas
- Make it a firewall
- Make it a protocol-aware proxy, with option to read and alter the parsed headers

---

## Notes
- The router listens to both bridges (`c1_iface` and `c2_iface`) and forwards packets between them
- If you change interface name or subnet in the Docker setup, update `self.interfaces`, `self.myIp`, and `routing_table.txt` accordingly
- For instructions on setting up or controlling the lab, see:  
  - [ansible/README.md](../ansible/README.md)
  - [docker/README.md](../docker/README.md)
  - [aliases-scripts/README.md](../aliases-scripts/README.md)

