from __future__ import annotations

from ipaddress import IPv4Address
from dataclasses import dataclass

from netaddr import EUI


@dataclass
class ArpTableEntry:
    """This class represents an ARP table entry in the ARP Table."""

    mac: EUI
    ip: IPv4Address
    c_type: str = "dynamic"
