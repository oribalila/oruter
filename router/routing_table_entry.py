from __future__ import annotations

from ipaddress import IPv4Address, IPv4Network
from dataclasses import dataclass


@dataclass
class RoutingTableEntry:
    """This class represents a routing table entry in the routing table."""

    network: IPv4Network
    next_hop: IPv4Address
    outgoing_interface: str
    metric: int = 100
