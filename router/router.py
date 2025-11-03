import copy
import subprocess

from socket import SOCK_RAW, AF_PACKET, htons, socket
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


class Router:
    """This class represents the router."""

    def __init__(self, routing_table_path: str | None = None):
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

    def capture_packet(self) -> None:
        """Captures packets and sends them for handling."""
        sock = socket(AF_PACKET, SOCK_RAW, htons(ETH_P_ALL))
        while True:
            bytes_packet, packet_metadata = sock.recvfrom(BUFFER_SIZE)
            interface = packet_metadata[0]
            if interface in self.interfaces:
                packet = Packet.bytes_constructor(bytes_packet)
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
            source_ip = packet.layers[1].source
            if source_ip in self.myIp.values():
                return
            self.handle_ipv4(packet, interface)
        elif (
            packet.layers[0].ether_type == ARP_CODE
            and packet.layers[1].target_protocol == self.myIp[interface]
        ):
            self.handle_arp(packet.layers[1], interface)

    def handle_arp(self, arp_header: ARP, interface: str) -> None:
        """Handles incoming ARP packet.

        Parameters:
            (Packet) arp_header:    The ARP packet
            (str) interface:        The incoming interface
        """
        self.arp_table.add(
            ArpTableEntry(arp_header.sender_hardware, arp_header.sender_protocol, "dynamic")
        )

        next_hop = self.get_next_hop(arp_header.sender_protocol)
        network = IPv4Network(f"{arp_header.sender_protocol}/32")
        self.routing_table.add(RoutingTableEntry(network, next_hop, interface))

        if arp_header.opcode == REQUEST_OPCODE:
            self.send_packet(self.build_arp_reply(interface, arp_header.sender_protocol), interface)

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
            self.send_packet(
                self.build_arp_request(output_interface, ip_header.destination),
                output_interface,
            )
            arp_requests_counter += 1
        if arp_requests_counter == MAXIMUM_ARP_REQUESTS:
            return

        if (
            isinstance(ipv4_payload, ICMP)
            and ipv4_payload.icmp_type == protocols.constants.icmp_constants.REQUEST_TYPE
            and ip_header.destination in self.myIp.values()
        ):
            self.send_packet(
                self.build_icmp_reply(ipv4_payload, ip_header.source, ip_header.destination),
                input_interface,
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
        ethernet_header = packet.layers[0]
        ip_header = packet.layers[1]
        ipv4_payload = packet.layers[2]

        interface = self.routing_table.find_interface(ip_header.destination)

        new_destination_mac = self.arp_table[ip_header.destination]
        new_source_mac = self.interface_mac[interface]
        new_ethernet_header = Ethernet(
            new_destination_mac, new_source_mac, ethernet_header.ether_type
        )
        new_ipv4_header = copy.copy(ip_header)
        new_ipv4_header.ttl -= 1
        packet = Packet([new_ethernet_header, new_ipv4_header, ipv4_payload])

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
    sock.send(packet)
    sock.close()
