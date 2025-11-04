import os
import copy
import json
import logging
import subprocess
import logging.config

from socket import SOCK_RAW, AF_PACKET, htons, socket
from pathlib import Path
from ipaddress import IPv4Address, IPv4Network
from threading import Thread
from collections.abc import Generator

from netaddr import EUI

from packet import Packet
from arp_table import ArpTable
from routing_table import RoutingTable
from arp_table_entry import ArpTableEntry
from routing_table_entry import RoutingTableEntry

import protocols.constants.icmp_constants
import protocols.constants.ipv4_constants

from protocols.arp import ARP
from protocols.icmp import ICMP
from protocols.ipv4 import IPv4
from protocols.ethernet import Ethernet
from protocols.constants.arp_constants import REPLY_OPCODE, REQUEST_OPCODE
from protocols.constants.global_constants import ARP_CODE, ETH_P_ALL, IPv4_CODE


BUFFER_SIZE = 65535
MAXIMUM_ARP_REQUESTS = 5
DEFAULT_MTU = 1500

log_dir = "logs"
directory = Path(__file__).resolve().parent
os.makedirs(directory / log_dir, exist_ok=True)

with open(directory / "logging_config.json") as logging_config_json:
    logging_config = json.load(logging_config_json)
    logging_config["handlers"]["file"]["filename"] = (
        directory / logging_config["handlers"]["file"]["filename"]
    )
    logging.config.dictConfig(logging_config)


logger = logging.getLogger(__name__)


class Router:
    """This class represents the router."""

    def __init__(self, routing_table_path: str | None = None):
        logger.info("Router initializing", extra={"context": None})
        self.arp_table = ArpTable()
        self.routing_table = RoutingTable(routing_table_path)
        self.myIp = {
            "c1_iface": IPv4Address("1.1.1.1"),
            "c2_iface": IPv4Address("2.2.2.1"),
        }
        self.interfaces = ["c1_iface", "c2_iface"]
        self.interface_mac = {}
        self.MTU = DEFAULT_MTU
        self.REAL_MTU = self.MTU + 14
        for interface in self.interfaces:
            mac = (
                str(
                    subprocess.run(
                        f"ip link show dev {interface}".split(), capture_output=True
                    ).stdout
                )
                .split("\\n")[1]
                .split()[1]
            )
            mac = EUI(mac)
            self.interface_mac[interface] = mac
        logger.debug(
            "Router initialized",
            extra={"context": {"interfaces": self.interfaces, "MTU": self.MTU}},
        )

    def capture_packet(self) -> None:
        """Captures packets and sends them for handling."""
        sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
        logger.info("Starting packet capture", extra={"context": {"interfaces": self.interfaces}})
        while True:
            bytes_packet, packet_metadata = sock.recvfrom(BUFFER_SIZE)
            interface = packet_metadata[0]
            if interface in self.interfaces:
                logger.debug("Captured packet", extra={"context": {"interface": interface}})
                logger.debug(
                    "Converting packet from bytes to object",
                    extra={"context": {"packet": bytes_packet, "interface": interface}},
                )
                packet = Packet.bytes_constructor(bytes_packet)
                logger.debug(
                    "Handling packet in a thread",
                    extra={"context": {"packet": packet, "interface": interface}},
                )
                thread = Thread(target=self.handle_packet, args=(packet, interface))
                thread.start()
        sock.close()

    def handle_packet(self, packet: Packet, interface: str) -> None:
        """Handles packet.

        Parameters:
            (Packet) packet: The packet to forward
            (str) interface: The incoming interface
        """
        if packet.layers[0].ether_type == IPv4_CODE:
            logger.debug(
                "Packet was classified as IPv4",
                extra={"context": {"packet": packet, "interface": interface}},
            )
            source_ip = packet.layers[1].source
            if source_ip in self.myIp.values():
                logger.debug(
                    "Stopping packet handling — packet originated from the router",
                    extra={"context": {"source_ip": source_ip}},
                )
                return
            logger.debug(
                "Handling IPv4 packet",
                extra={"context": {"packet": packet, "interface": interface}},
            )
            self.handle_ipv4(packet, interface)
        elif (
            packet.layers[0].ether_type == ARP_CODE
            and packet.layers[1].target_protocol == self.myIp[interface]
        ):
            logger.debug(
                "Packet was classified as an ARP for the router",
                extra={
                    "context": {
                        "ether_type": packet.layers[0].ether_type,
                        "target_protocol": packet.layers[1].target_protocol,
                    }
                },
            )
            self.handle_arp(packet.layers[1], interface)
        else:
            logger.warning(
                "No handler for frame",
                extra={"context": {"ether_type": packet.layers[0].ether_type, "packet": packet}},
            )

    def handle_arp(self, arp_header: ARP, interface: str) -> None:
        """Handles incoming ARP packet.

        Parameters:
            (Packet) arp_header:    The ARP packet
            (str) interface:        The incoming interface
        """
        arp_table_entry = ArpTableEntry(
            arp_header.sender_hardware, arp_header.sender_protocol, "dynamic"
        )
        logger.debug("Updating ARP table", extra={"context": {"entry": arp_table_entry}})
        self.arp_table.add(arp_table_entry)

        next_hop = self.get_next_hop(arp_header.sender_protocol)
        network = IPv4Network(f"{arp_header.sender_protocol}/32")
        routing_table_entry = RoutingTableEntry(network, next_hop, interface)
        logger.debug("Updating routing table", extra={"context": {"entry": routing_table_entry}})
        self.routing_table.add(routing_table_entry)

        if arp_header.opcode == REQUEST_OPCODE:
            arp_reply_packet = self.build_arp_reply(interface, arp_header.sender_protocol)
            logger.debug(
                "Packet is an ARP request. Sending ARP reply",
                extra={"context": {"opcode": arp_header.opcode, "packet": arp_reply_packet}},
            )
            self.send_packet(arp_reply_packet, interface)

    def handle_ipv4(self, packet: Packet, input_interface: str) -> None:
        """Handles incoming IPv4 packet.

        Parameters:
            (Packet) packet: The IPv4 packet
            (str) interface: The incoming interface
        """
        ethernet_header = packet.layers[0]
        ip_header = packet.layers[1]
        ipv4_payload = packet.layers[2]

        arp_requests_counter = 0
        while (
            ip_header.source not in self.arp_table and arp_requests_counter < MAXIMUM_ARP_REQUESTS
        ):
            logger.debug(
                "Sender IP is not in the ARP table. Sending an ARP request",
                extra={"context": {"source_ip": ip_header.source}},
            )
            self.send_packet(
                self.build_arp_request(input_interface, ip_header.source),
                input_interface,
            )
            arp_requests_counter += 1

        output_interface = self.routing_table.find_interface(ip_header.destination)
        arp_requests_counter = 0
        while (
            ip_header.destination not in self.arp_table
            and arp_requests_counter < MAXIMUM_ARP_REQUESTS
        ):
            logger.debug(
                "Destination IP is not in the ARP table. Sending an ARP request",
                extra={"context": {"destination_ip": ip_header.destination}},
            )
            self.send_packet(
                self.build_arp_request(output_interface, ip_header.destination),
                output_interface,
            )
            arp_requests_counter += 1
        if arp_requests_counter == MAXIMUM_ARP_REQUESTS:
            logger.warning(
                "Sent too much ARP requests without finding target MAC address. Aborting",
                extra={
                    "context": {
                        "arp_requests_counter": arp_requests_counter,
                        "output_interface": output_interface,
                    }
                },
            )
            return

        if (
            isinstance(ipv4_payload, ICMP)
            and ipv4_payload.icmp_type == protocols.constants.icmp_constants.REQUEST_TYPE
            and ip_header.destination in self.myIp.values()
        ):
            logger.info(
                "Identified packet as an ICMP echo request for the router",
                extra={"context": {"destination_ip": ip_header.destination}},
            )
            icmp_reply = self.build_icmp_reply(
                ipv4_payload, ip_header.source, ip_header.destination
            )
            self.send_packet(
                icmp_reply,
                input_interface,
            )
            logger.info(
                "Sending an ICMP echo reply",
                extra={"context": {"destination_ip": icmp_reply.layers[1].destination}},
            )
            return

        source_ip_network = self.routing_table.find_network(ip_header.source)
        if (
            ip_header.destination not in source_ip_network
            and ethernet_header.source not in self.interface_mac.values()
        ):
            self.forward_ipv4(packet)

    def forward_ipv4(self, packet: Packet) -> None:
        """Forwards an IPv4 packet.

        Parameters:
            (Packet) packet: The packet to forward
        """
        logger.info("Forwarding packet", extra={"context": {"packet": packet}})
        ethernet_header = packet.layers[0]
        ip_header = packet.layers[1]
        ipv4_payload = packet.layers[2]

        interface = self.routing_table.find_interface(ip_header.destination)
        logger.debug(
            "Found packet destination interface for forwarding",
            extra={"context": {"interface": interface}},
        )

        new_destination_mac = self.arp_table[ip_header.destination]
        new_source_mac = self.interface_mac[interface]
        new_ethernet_header = Ethernet(
            new_destination_mac, new_source_mac, ethernet_header.ether_type
        )
        new_ipv4_header = copy.copy(ip_header)
        new_ipv4_header.ttl -= 1
        packet = Packet([new_ethernet_header, new_ipv4_header, ipv4_payload])
        logger.debug("Altered packet", extra={"context": {"altered_packet": packet}})

        logger.debug(
            "Forwarding packet", extra={"context": {"packet": packet, "interface": interface}}
        )
        self.send_packet(packet, interface)

    def get_next_hop(self, dest_ip: IPv4Address) -> IPv4Address:
        """Get the next hop of dest_ip.

        Parameters:
            (IPv4Address) dest_ip: The destination ip we wants to get its next hop for forwarding

        Return:
            (IPv4Address): The next hop
        """
        network = self.routing_table.find_network(dest_ip)
        for ip in self.arp_table:
            if ip in network:
                return ip

    def fragment_packet(self, packet: Packet) -> Generator[bytes, None, None]:
        """Fragments packets.

        Parameters:
            (Packet) packet: The IPv4 packet to fragment

        Return:
            (generator): A generator of the fragments
        """
        logger.info(
            "Fragmenting packet", extra={"context": {"packet": packet, "packet_size": len(packet)}}
        )
        if not isinstance(packet.layers[1], IPv4):
            raise TypeError("Not an IPv4 packet")

        ipv4_header = packet.layers[1]
        ipv4_payload_bytes = b"".join(map(bytes, packet.layers[2:]))

        payload_MTU = self.MTU - ipv4_header.header_length
        payload_MTU = (payload_MTU // 8) * 8
        num_fragments = (len(ipv4_payload_bytes) + payload_MTU - 1) // payload_MTU
        for i in range(num_fragments):
            start = i * payload_MTU
            end = min(start + payload_MTU, len(packet))
            fragment_data = ipv4_payload_bytes[start:end]

            flags = (
                protocols.constants.ipv4_constants.Flags.MORE_FRAGMENTS
                if i != num_fragments - 1
                else 0b000
            )

            new_ipv4_header = copy.copy(ipv4_header)
            new_ipv4_header.total_length = new_ipv4_header.header_length + len(fragment_data)
            new_ipv4_header.flags = flags
            new_ipv4_header.fragment_offset = start

            fragment = bytes(new_ipv4_header) + fragment_data
            logger.debug("Fragment was created", extra={"context": {"fragment": fragment}})
            yield fragment

    def build_arp_request(self, interface: str, target_ip: IPv4Address):
        """Builds ARP request packet.

        Parameters:
            (str) interface:            The interface in which the reply will be sent through (for getting the interface MAC and IP)
            (IPv4Address) target_ip:    The target IP

        Return:
            (Packet): The ARP request packet
        """
        sender_mac = self.interface_mac[interface]
        sender_ip = self.myIp[interface]
        target_mac = EUI("00-00-00-00-00-00")

        dest_mac = EUI("FF-FF-FF-FF-FF-FF")
        arp_request_header = ARP(
            opcode=REQUEST_OPCODE,
            sender_hardware=sender_mac,
            sender_protocol=sender_ip,
            target_hardware=target_mac,
            target_protocol=target_ip,
        )
        ethernet_header = Ethernet(dest_mac, sender_mac, ARP_CODE)
        return Packet.bytes_constructor(bytes(ethernet_header) + bytes(arp_request_header))

    def build_arp_reply(self, interface: str, target_ip: IPv4Address):
        """Builds ARP reply packet.

        Parameters:
            (str) interface:            The interface in which the reply will be sent through (for getting the interface MAC and IP)
            (IPv4Address) target_ip:    The target IP

        Return:
            (Packet): The ARP reply packet
        """
        sender_mac = self.interface_mac[interface]
        sender_ip = self.myIp[interface]
        target_mac = self.arp_table[target_ip]

        arp_reply_header = ARP(
            opcode=REPLY_OPCODE,
            sender_hardware=sender_mac,
            sender_protocol=sender_ip,
            target_hardware=target_mac,
            target_protocol=target_ip,
        )
        ethernet_header = Ethernet(target_mac, sender_mac, ARP_CODE)
        return Packet.bytes_constructor(bytes(ethernet_header) + bytes(arp_reply_header))

    def build_icmp_reply(
        self, icmp_header: ICMP, destination_ip: IPv4Address, source_ip: IPv4Address
    ) -> Packet:
        """Builds ICMP reply from ICMP request packet.

        Return:
            (ICMP): icmp reply for the icmp request (self)

        Raise:
            (AttributeError): When the packet is not an ICMP request
        """
        # if self.layers[0].ether_type != global_constants.IPv4_CODE or self.layers[1].protocol != ipv4_constants.ICMP_CODE or self.layers[2].icmp_type != icmp_constants.REQUEST_TYPE:
        #     raise AttributeError('Received packet is not an ICMP request')

        interface = list(self.myIp.keys())[list(self.myIp.values()).index(source_ip)]
        sender_mac = self.interface_mac[interface]
        target_mac = self.arp_table[destination_ip]
        ethernet_header = Ethernet(target_mac, sender_mac, IPv4_CODE)

        icmp_reply_header = icmp_header.build_icmp_reply_header()
        ip_header = IPv4(
            protocol=protocols.constants.ipv4_constants.ICMP_CODE,
            destination=destination_ip,
            source=source_ip,
        )
        ip_header.total_length += len(icmp_reply_header)

        icmp_reply = Packet([ethernet_header, ip_header, icmp_reply_header])
        return icmp_reply

    def send_packet(self, packet: Packet, interface: str) -> None:
        """Sends packet over an interface.

        Parameters:
            (Packet) packet: The packet to send
            (str) interface: The interface to send to packet over it
        """
        if len(packet) <= self.REAL_MTU:
            send_bytes_packet(bytes(packet), interface)
        elif (
            isinstance(packet.layers[1], IPv4)
            and not packet.layers[1].flags & protocols.constants.ipv4_constants.Flags.DONT_FRAGMENT
        ):
            fragments = self.fragment_packet(packet)
            for fragment in fragments:
                fragment = bytes(packet.layers[0]) + fragment
                send_bytes_packet(fragment, interface)


def send_bytes_packet(packet: bytes, interface: str) -> None:
    """Sends packet over an interface.

    Parameters:
        (bytes) packet: The packet to send
        (str) interface: The interface to send to packet over it
    """
    sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
    sock.bind((interface, 0))
    logger.debug("Sending packet", extra={"context": {"packet": packet, "interface": interface}})
    sock.send(packet)
    sock.close()
