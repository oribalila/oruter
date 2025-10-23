from __future__ import annotations

import struct

from ipaddress import IPv4Address
from dataclasses import dataclass

from netaddr import EUI

from protocols.constants.arp_constants import (
    OPCODE,
    ETHERNET_TYPE,
    HARDWARE_SIZE,
    HARDWARE_TYPE,
    PROTOCOL_SIZE,
    PROTOCOL_TYPE,
    SENDER_HARDWARE,
    SENDER_PROTOCOL,
    TARGET_HARDWARE,
    TARGET_PROTOCOL,
)
from protocols.constants.global_constants import MAC_SIZE, IPv4_CODE, IPv4_SIZE


@dataclass
class ARP:
    """This class represents and handles ARP header."""

    hardware_type: int = ETHERNET_TYPE
    protocol_type: int = IPv4_CODE
    hardware_size: int = MAC_SIZE
    protocol_size: int = IPv4_SIZE
    opcode: int = None
    sender_hardware: EUI = None
    sender_protocol: IPv4Address = None
    target_hardware: EUI = None
    target_protocol: IPv4Address = None

    def __setattr__(self, name, value):
        """Regular setattr, but also validates the parameters.

        Raise:
            (AttributeError): When an attribute is None
        """
        if value is None:
            raise AttributeError(f"{name} can't be None")
        object.__setattr__(self, name, value)

    @classmethod
    def bytes_constructor(cls, header: bytes) -> ARP:
        """Constructs header from its bytes representation.

        Parameters:
            (Packet) header: The header's bytes representation

        Return:
            (ARP): The constructed header
        """
        hardware_type = int(header[HARDWARE_TYPE.index :][: HARDWARE_TYPE.size].hex(), 16)
        protocol_type = int(header[PROTOCOL_TYPE.index :][: PROTOCOL_TYPE.size].hex(), 16)
        hardware_size = int(header[HARDWARE_SIZE.index :][: HARDWARE_SIZE.size].hex(), 16)
        protocol_size = int(header[PROTOCOL_SIZE.index :][: PROTOCOL_SIZE.size].hex(), 16)
        opcode = int(header[OPCODE.index :][: OPCODE.size].hex(), 16)
        sender_hardware = EUI(header[SENDER_HARDWARE.index :][: SENDER_HARDWARE.size].hex())
        sender_protocol = IPv4Address(header[SENDER_PROTOCOL.index :][: SENDER_PROTOCOL.size])
        target_hardware = EUI(header[TARGET_HARDWARE.index :][: TARGET_HARDWARE.size].hex())
        target_protocol = IPv4Address(header[TARGET_PROTOCOL.index :][: TARGET_PROTOCOL.size])
        return cls(
            hardware_type,
            protocol_type,
            hardware_size,
            protocol_size,
            opcode,
            sender_hardware,
            sender_protocol,
            target_hardware,
            target_protocol,
        )

    def __bytes__(self) -> bytes:
        arp_header = struct.pack(
            "!HHBBH6s4s6s4s",
            self.hardware_type,
            self.protocol_type,
            self.hardware_size,
            self.protocol_size,
            self.opcode,
            int(self.sender_hardware).to_bytes(MAC_SIZE, "big"),
            int(self.sender_protocol).to_bytes(IPv4_SIZE, "big"),
            int(self.target_hardware).to_bytes(MAC_SIZE, "big"),
            int(self.target_protocol).to_bytes(IPv4_SIZE, "big"),
        )
        return arp_header
