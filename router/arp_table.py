from ipaddress import IPv4Address
from dataclasses import field, dataclass

from arp_table_entry import ArpTableEntry


@dataclass
class ArpTable:
    """This class represents and handles the ARP table in the router."""

    entries: list[ArpTableEntry] = field(default_factory=list)

    def __getitem__(self, key):
        key = IPv4Address(key)
        for entry in self.entries:
            if entry.ip == key:
                return entry.mac

    def __contains__(self, key):
        return key in self.keys()

    def __iter__(self):
        return self.keys()

    def keys(self):
        for entry in self.entries:
            yield entry.ip

    def add(self, entry: ArpTableEntry):
        if not isinstance(entry, ArpTableEntry):
            raise TypeError("Not an ArpTableEntry")
        if entry not in self.entries:
            self.entries.append(entry)
            if entry.c_type == "static":
                del self.entries[-1]
                self.entries.insert(0, entry)

    def remove(self, entry: ArpTableEntry):
        if not isinstance(entry, ArpTableEntry):
            raise TypeError("Not an ArpTableEntry")
        try:
            self.entries.remove(entry)
        except ValueError as ve:
            print(ve)
