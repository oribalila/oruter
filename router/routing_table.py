from ipaddress import IPv4Address, IPv4Network
from collections.abc import Generator

from routing_table_entry import RoutingTableEntry

from protocols.constants.global_constants import MAXIMUM_NETMASK


class RoutingTable:
    """This class represents and handles the routing table in the router."""

    def __init__(self, file: str | None = None):
        self.entries: list[RoutingTableEntry] = []
        if file is not None:
            with open(file) as configuration:
                for line in configuration:
                    values = line.split()
                    network = IPv4Network(values[0])
                    next_hop = IPv4Address(values[1])
                    interface = values[2]
                    metric = values[3]
                    self.entries.append(RoutingTableEntry(network, next_hop, interface, metric))

    def __getitem__(self, key):
        key = IPv4Network(key)
        for entry in self.entries:
            if entry.network == key:
                return [entry.next_hop, entry.outgoing_interface]

    def add(self, entry: RoutingTableEntry):
        if not isinstance(entry, RoutingTableEntry):
            raise TypeError("Not a RoutingTableEntry")

        entry_network_id = entry.network.network_address
        for network in self.networks:
            if entry_network_id in network and entry.outgoing_interface == self.find_interface(
                entry_network_id
            ):
                return
        self.entries.append(entry)

    def remove(self, entry: RoutingTableEntry):
        if not isinstance(entry, RoutingTableEntry):
            raise TypeError("Not a RoutingTableEntry")
        try:
            self.entries.remove(entry)
        except ValueError as ve:
            print(ve)

    @property
    def networks(self) -> Generator[IPv4Network, None, None]:
        """Gets a generator of the networks that the routing table acknowledges.

        Return:
            (generator): A generator of all the networks the routing table acknowledges.
        """
        for entry in self.entries:
            yield entry.network

    def find_interface(self, destination_ip: IPv4Address) -> str:
        """Get the interface a packet destined to destination_ip should be sent into.

        Parameters:
            (IPv4Address) destination_ip: The IP address which we want to find what interface has the smallest network it belongs to

        Return:
            (IPv4Address): The interface in which the packet with destination ip of destination_ip should be send through according to the routing table
        """
        cur_netmask = MAXIMUM_NETMASK
        for entry in self.entries:
            if destination_ip in entry.network:
                netmask = int(entry.network.hostmask)
                if netmask <= cur_netmask:
                    cur_netmask = netmask
                    outgoing_interface = entry.outgoing_interface
        return outgoing_interface

    def find_network(self, destination_ip: IPv4Address) -> IPv4Network:
        """Get the smallest network identifier (that the routing table acknowledges) a packet destined to destination_ip belongs to.

        Parameters:
            (IPv4Address) destination_ip: The IP address which we want to find what network (the smallest) it belongs to

        Return:
            (IPv4Network): The matching network.
        """
        cur_netmask = int(IPv4Network("0.0.0.0/0").hostmask)
        for entry in self.entries:
            if destination_ip in entry.network:
                netmask = int(entry.network.hostmask)
                if netmask <= cur_netmask:
                    cur_netmask = netmask
                    smallest_network = entry.network
        return smallest_network
