import sys

from pathlib import Path

from netaddr import EUI


sys.path.append(str(Path(__file__).resolve().parent.parent))
from protocols.ethernet import Ethernet


# -- Ethernet + ARP --
arp_ethernet_headers = [
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("13-9D-10-F4-10-54"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("3E-A5-89-2E-56-7C"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("6B-4E-6C-4B-CD-C0"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("4A-72-0F-70-9E-01"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("E2-B8-C5-80-D5-9D"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("6B-E4-E8-11-9F-F8"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("F8-C9-F6-B3-F1-8B"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("AF-84-40-62-77-DB"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("29-22-BB-CF-26-28"),
        ether_type=2054,
    ),
    Ethernet(
        destination=EUI("FF-FF-FF-FF-FF-FF"),
        source=EUI("4A-48-C2-F6-1D-A4"),
        ether_type=2054,
    ),
]
arp_ethernet_headers_bytes = [
    b"\xff\xff\xff\xff\xff\xff\x13\x9d\x10\xf4\x10T\x08\x06",
    b"\xff\xff\xff\xff\xff\xff>\xa5\x89.V|\x08\x06",
    b"\xff\xff\xff\xff\xff\xffkNlK\xcd\xc0\x08\x06",
    b"\xff\xff\xff\xff\xff\xffJr\x0fp\x9e\x01\x08\x06",
    b"\xff\xff\xff\xff\xff\xff\xe2\xb8\xc5\x80\xd5\x9d\x08\x06",
    b"\xff\xff\xff\xff\xff\xffk\xe4\xe8\x11\x9f\xf8\x08\x06",
    b"\xff\xff\xff\xff\xff\xff\xf8\xc9\xf6\xb3\xf1\x8b\x08\x06",
    b"\xff\xff\xff\xff\xff\xff\xaf\x84@bw\xdb\x08\x06",
    b'\xff\xff\xff\xff\xff\xff)"\xbb\xcf&(\x08\x06',
    b"\xff\xff\xff\xff\xff\xffJH\xc2\xf6\x1d\xa4\x08\x06",
]

# -- Ethernet + IPv4 + ICMP --
ipv4_ethernet_headers = [
    Ethernet(
        destination=EUI("08-96-D8-69-6D-46"),
        source=EUI("F4-59-A3-A8-2C-B4"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("F4-59-A3-A8-2C-B4"),
        source=EUI("38-43-50-3A-32-66"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("38-43-50-3A-32-66"),
        source=EUI("04-E5-06-E6-F7-C6"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("04-E5-06-E6-F7-C6"),
        source=EUI("44-55-F5-48-F5-78"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("44-55-F5-48-F5-78"),
        source=EUI("A4-01-3F-24-4A-C0"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("A4-01-3F-24-4A-C0"),
        source=EUI("BB-95-14-7B-E1-06"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("BB-95-14-7B-E1-06"),
        source=EUI("C2-87-E5-16-5B-C9"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("C2-87-E5-16-5B-C9"),
        source=EUI("DF-BE-16-0A-6E-8A"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("DF-BE-16-0A-6E-8A"),
        source=EUI("39-2E-D9-0A-9B-36"),
        ether_type=2048,
    ),
    Ethernet(
        destination=EUI("39-2E-D9-0A-9B-36"),
        source=EUI("15-7F-2F-09-6A-53"),
        ether_type=2048,
    ),
]
ipv4_ethernet_headers_bytes = [
    b"\x08\x96\xd8imF\xf4Y\xa3\xa8,\xb4\x08\x00",
    b"\xf4Y\xa3\xa8,\xb48CP:2f\x08\x00",
    b"8CP:2f\x04\xe5\x06\xe6\xf7\xc6\x08\x00",
    b"\x04\xe5\x06\xe6\xf7\xc6DU\xf5H\xf5x\x08\x00",
    b"DU\xf5H\xf5x\xa4\x01?$J\xc0\x08\x00",
    b"\xa4\x01?$J\xc0\xbb\x95\x14{\xe1\x06\x08\x00",
    b"\xbb\x95\x14{\xe1\x06\xc2\x87\xe5\x16[\xc9\x08\x00",
    b"\xc2\x87\xe5\x16[\xc9\xdf\xbe\x16\nn\x8a\x08\x00",
    b"\xdf\xbe\x16\nn\x8a9.\xd9\n\x9b6\x08\x00",
    b"9.\xd9\n\x9b6\x15\x7f/\tjS\x08\x00",
]
