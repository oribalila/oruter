from __future__ import annotations

import struct

from socket import inet_aton
from ipaddress import IPv4Address
from dataclasses import dataclass

from protocols.constants.ipv4_constants import (
    DSF,
    TTL,
    FLAGS,
    SOURCE,
    VERSION,
    PROTOCOL,
    FLAGS_MASK,
    DEFAULT_DSF,
    DESTINATION,
    INITIAL_TTL,
    TOTAL_LENGTH,
    HEADER_LENGTH,
    IDENTIFICATION,
    FRAGMENT_OFFSET,
    HEADER_CHECKSUM,
    HEADER_LENGTH_MASK,
    FRAGMENT_OFFSET_MASK,
    MINIMUM_HEADER_LENGTH,
    HEADER_LENGTH_MULTIPLIER,
    FRAGMENT_OFFSET_BITS_SIZE,
    FRAGMENT_OFFSET_MULTIPLIER,
    Flags,
)


@dataclass
class IPv4:
    """This class represents and handles an IPv4 header."""

    header_length: int = MINIMUM_HEADER_LENGTH
    dsf: int = DEFAULT_DSF
    total_length: int = MINIMUM_HEADER_LENGTH
    identification: int = 0
    flags: int = Flags.DONT_FRAGMENT
    fragment_offset: int = 0
    ttl: int = INITIAL_TTL
    protocol: int = None
    checksum: int = 0
    source: IPv4Address = None
    destination: IPv4Address = None
    options: bytes = b""

    def __setattr__(self, name, value):
        """Regular setattr, but also updates the checksum and validates the parameters.

        Raise:
            (AttributeError): When an attribute is None
        """
        # total_length == MINIMUM_HEADER_LENGTH represents that there is no payload, so we set it to header_length
        if name == "total_length" and value == MINIMUM_HEADER_LENGTH:
            value = self.header_length
        if value is None:
            raise AttributeError(f"{name} can't be None")
        object.__setattr__(self, name, value)

    @classmethod
    def bytes_constructor(cls, header: bytes) -> IPv4:
        """Constructs header from its bytes representation.

        Parameters:
            (Packet) header: The header's bytes representation

        Return:
            (IPv4): The constructed header
        """
        header_length = IPv4.get_header_length(header)
        dsf = int(header[DSF.index :][: DSF.size].hex(), 16)
        total_length = int(header[TOTAL_LENGTH.index :][: TOTAL_LENGTH.size].hex(), 16)
        identification = int(header[IDENTIFICATION.index :][: IDENTIFICATION.size].hex(), 16)
        flags = IPv4.get_flags(header)
        fragment_offset = IPv4.get_fragment_offset(header)
        ttl = int(header[TTL.index :][: TTL.size].hex(), 16)
        protocol = int(header[PROTOCOL.index :][: PROTOCOL.size].hex(), 16)
        checksum = int(header[HEADER_CHECKSUM.index :][: HEADER_CHECKSUM.size].hex(), 16)
        source = IPv4Address(header[SOURCE.index :][: SOURCE.size])
        destination = IPv4Address(header[DESTINATION.index :][: DESTINATION.size])
        options = header[MINIMUM_HEADER_LENGTH:]
        return cls(
            header_length,
            dsf,
            total_length,
            identification,
            flags,
            fragment_offset,
            ttl,
            protocol,
            checksum,
            source,
            destination,
            options,
        )

    @staticmethod
    def get_header_length(header: bytes):
        """Returns the header length from bytes representation of IPv4 Header.

        Parameters:
            (bytes) header: The IPv4 header

        Return:
            (int): The header length
        """
        return (header[HEADER_LENGTH.index] & HEADER_LENGTH_MASK) * HEADER_LENGTH_MULTIPLIER

    @staticmethod
    def get_flags(header: bytes):
        """Returns the flags offset from bytes representation of IPv4 Header.

        Parameters:
            (bytes) header: The IPv4 header

        Return:
            (int): The flags
        """
        return (
            int(header[FLAGS.index :][: FLAGS.size].hex(), 16) & FLAGS_MASK
        ) >> FRAGMENT_OFFSET_BITS_SIZE

    @staticmethod
    def get_fragment_offset(header: bytes):
        """Returns the fragment offset from bytes representation of IPv4 Header.

        Parameters:
            (bytes) header: The IPv4 header

        Return:
            (int): The fragment offset
        """
        return (
            int(header[FRAGMENT_OFFSET.index :][: FRAGMENT_OFFSET.size].hex(), 16)
            & FRAGMENT_OFFSET_MASK
        ) * FRAGMENT_OFFSET_MULTIPLIER

    def __bytes__(self) -> bytes:
        flags = self.flags << FRAGMENT_OFFSET_BITS_SIZE
        header_length = self.header_length // HEADER_LENGTH_MULTIPLIER
        fragment_offset = self.fragment_offset // FRAGMENT_OFFSET_MULTIPLIER
        ipv4_header = (
            struct.pack(
                "!BBHH2sBBH4s4s",
                (VERSION + header_length),
                self.dsf,
                self.total_length,
                self.identification,
                (flags + fragment_offset).to_bytes(2, "big"),
                self.ttl,
                self.protocol,
                self.checksum,
                inet_aton(str(self.source)),
                inet_aton(str(self.destination)),
            )
            + self.options
        )
        return ipv4_header

    def __len__(self) -> int:
        return len(bytes(self))
