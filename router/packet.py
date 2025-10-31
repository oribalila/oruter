from __future__ import annotations

from dataclasses import dataclass

import protocols.constants.ipv4_constants
import protocols.constants.global_constants

from protocols.arp import ARP
from protocols.icmp import ICMP
from protocols.ipv4 import IPv4
from protocols.ethernet import Ethernet


@dataclass
class Packet:
    """This class represents and handles a packet, including all of its layers from layer 2."""

    layers: list

    @classmethod
    def bytes_constructor(cls, packet: bytes):
        """Constructs a packet from its bytes representation.

        Parameters:
            (Packet) packet: The packet's bytes representation

        Return:
            (Packet): The constructed packet
        """
        layers = []
        ethernet_header = Ethernet.bytes_constructor(
            packet[: protocols.constants.global_constants.THIRD_LAYER_INDEX]
        )
        layers.append(ethernet_header)
        if ethernet_header.ether_type == protocols.constants.global_constants.IPv4_CODE:
            ip_packet = packet[protocols.constants.global_constants.THIRD_LAYER_INDEX :]
            header_length = IPv4.get_header_length(ip_packet)
            ip_header = IPv4.bytes_constructor(ip_packet[:header_length])
            layers.append(ip_header)
            # We don't want to treat any fragmented packet as any other protocol.
            if (
                ip_header.flags & protocols.constants.ipv4_constants.Flags.MORE_FRAGMENTS
                or ip_header.fragment_offset
            ):
                layers.append(ip_packet[header_length:])
            elif ip_header.protocol == protocols.constants.ipv4_constants.ICMP_CODE:
                icmp_header = ICMP.bytes_constructor(ip_packet[header_length:])
                layers.append(icmp_header)
            else:
                layers.append(ip_packet[header_length:])
        elif ethernet_header.ether_type == protocols.constants.global_constants.ARP_CODE:
            arp_header = ARP.bytes_constructor(
                packet[protocols.constants.global_constants.THIRD_LAYER_INDEX :]
            )
            layers.append(arp_header)
        else:
            layers.append(packet[protocols.constants.global_constants.THIRD_LAYER_INDEX :])
        return cls(layers)

    def __bytes__(self):
        return b"".join(map(bytes, self.layers))

    def __len__(self):
        return len(bytes(self))
