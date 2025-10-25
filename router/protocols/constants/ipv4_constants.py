from enum import IntFlag

from protocols.constants.header_field import HeaderField


ICMP_CODE = 1

VERSION = 4 << 4  # uses only the 4 leftmost bits of the version field
MINIMUM_HEADER_LENGTH = 20
DEFAULT_DSF = 0
INITIAL_TTL = 64

HEADER_LENGTH = HeaderField(index=0, size=1)
DSF = HeaderField(index=1, size=1)
TOTAL_LENGTH = HeaderField(index=2, size=2)
IDENTIFICATION = HeaderField(index=4, size=2)
FLAGS = HeaderField(index=6, size=2)
FRAGMENT_OFFSET = HeaderField(index=6, size=2)
TTL = HeaderField(index=8, size=1)
PROTOCOL = HeaderField(index=9, size=1)
HEADER_CHECKSUM = HeaderField(index=10, size=2)
SOURCE = HeaderField(index=12, size=4)
DESTINATION = HeaderField(index=16, size=4)

HEADER_LENGTH_MASK = 0b00001111
HEADER_LENGTH_BITS_SIZE = 4
FLAGS_MASK = 0b1110000000000000
FRAGMENT_OFFSET_MASK = 0b0001111111111111
FRAGMENT_OFFSET_BITS_SIZE = 13
HEADER_LENGTH_MULTIPLIER = 4
FRAGMENT_OFFSET_MULTIPLIER = 8


# Flags:
class Flags(IntFlag):
    DONT_FRAGMENT = 0b010
    MORE_FRAGMENTS = 0b001
