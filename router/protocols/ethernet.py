from __future__ import annotations

import struct

from dataclasses import dataclass

from netaddr import EUI

import protocols.constants.global_constants
import protocols.constants.ethernet_constants


@dataclass
class Ethernet:
    """This class represents and handles Ethernet header."""

    destination: EUI
    source: EUI
    ether_type: int

    @classmethod
    def bytes_constructor(cls, header: bytes) -> Ethernet:
        """Constructs header from its bytes representation.

        Parameters:
            (Packet) header: The header's bytes representation

        Return:
            (Ethernet): The constructed header
        """
        destination = EUI(header[: protocols.constants.global_constants.MAC_SIZE].hex())
        source = EUI(
            header[protocols.constants.ethernet_constants.SOURCE.index :][
                : protocols.constants.global_constants.MAC_SIZE
            ].hex()
        )
        ether_type = int(
            header[protocols.constants.ethernet_constants.ETHER_TYPE.index :][
                : protocols.constants.ethernet_constants.ETHER_TYPE.size
            ].hex(),
            16,
        )
        return cls(destination, source, ether_type)

    def __bytes__(self) -> bytes:
        return struct.pack(
            "!6s6sH",
            int(self.destination).to_bytes(protocols.constants.global_constants.MAC_SIZE, "big"),
            int(self.source).to_bytes(protocols.constants.global_constants.MAC_SIZE, "big"),
            self.ether_type,
        )
