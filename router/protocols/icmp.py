from __future__ import annotations

import copy
import time
import struct

from itertools import cycle
from dataclasses import field, dataclass

from protocols.ipv4 import IPv4
from protocols.constants.icmp_constants import (
    CODE,
    DATA,
    CHECKSUM,
    ICMP_TYPE,
    TIMESTAMP,
    IDENTIFIER,
    REPLY_TYPE,
    SEQUENCE_NUMBER,
)


current_identifier = cycle(range(0, int.from_bytes(b"\xff" * IDENTIFIER.size) + 1))


def get_time_bytes():
    return int(time.time()).to_bytes(8, "little")


@dataclass
class ICMP:
    """This class represents and handles an ICMP header."""

    icmp_type: int
    code: int = 0
    checksum: int = 0
    identifier: int = field(default_factory=current_identifier.__next__)
    sequence_number: int = 1
    timestamp: bytes = field(default_factory=get_time_bytes)
    data: bytes = b"supercyberdevopsnetworkingaiquatumgitopsanswer42"

    @classmethod
    def bytes_constructor(cls, header: bytes) -> ICMP:
        """Constructs header from its bytes representation.

        Parameters:
            (Packet) header: The header's bytes representation

        Return:
            (ICMP): The constructed header
        """
        icmp_type = int(header[ICMP_TYPE.index :][: ICMP_TYPE.size].hex(), 16)
        code = int(header[CODE.index :][: CODE.size].hex(), 16)
        checksum = int(header[CHECKSUM.index :][: CHECKSUM.size].hex(), 16)
        identifier = int(header[IDENTIFIER.index :][: IDENTIFIER.size].hex(), 16)
        sequence_number = int(header[SEQUENCE_NUMBER.index :][: SEQUENCE_NUMBER.size].hex(), 16)
        timestamp = int(header[TIMESTAMP.index :][: TIMESTAMP.size].hex(), 16).to_bytes(8, "big")
        data = header[DATA.index :]
        return cls(icmp_type, code, checksum, identifier, sequence_number, timestamp, data)

    def __setattr__(self, name, value):
        """Regular setattr, but also updates the checksum and validates the parameters.

        Raise:
            (ValueError): When this is an initialization and checksum is wrong
            (AttributeError): When an attribute is None
        """
        NUMBER_OF_ATTRIBUTES = self.__init__.__code__.co_argcount - 1  # 7
        is_init = False
        if len(vars(self)) < NUMBER_OF_ATTRIBUTES:
            is_init = True
        if value is None:
            raise AttributeError(f"{name} can't be None")
        object.__setattr__(self, name, value)
        if len(vars(self)) == NUMBER_OF_ATTRIBUTES:
            if self.checksum != 0 and is_init:
                correct_checksum_header = copy.copy(self)
                correct_checksum_header.checksum = 0
                if self.checksum != correct_checksum_header.checksum:
                    raise ValueError("Checksum is wrong")
            object.__setattr__(self, "checksum", 0)
            checksum = IPv4.calculate_internet_checksum(bytes(self))
            object.__setattr__(self, "checksum", checksum)

    def __bytes__(self) -> bytes:
        icmp_header = struct.pack(
            f"!BBHHH8s{len(self.data)}s",
            self.icmp_type,
            self.code,
            self.checksum,
            self.identifier,
            self.sequence_number,
            self.timestamp,
            self.data,
        )
        return icmp_header

    def __len__(self) -> int:
        return len(bytes(self))

    def build_icmp_reply_header(self) -> ICMP:
        """Builds ICMP reply header from ICMP request header.

        Return:
            (ICMP): icmp reply header for the icmp request (self)
        """
        icmp_reply_header = copy.copy(self)
        icmp_reply_header.icmp_type = REPLY_TYPE

        return icmp_reply_header
