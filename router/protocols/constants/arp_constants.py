from protocols.constants.header_field import HeaderField


ETHERNET_TYPE = 1
REQUEST_OPCODE = 1
REPLY_OPCODE = 2

HARDWARE_TYPE = HeaderField(index=0, size=2)
PROTOCOL_TYPE = HeaderField(index=2, size=2)
HARDWARE_SIZE = HeaderField(index=4, size=1)
PROTOCOL_SIZE = HeaderField(index=5, size=1)
OPCODE = HeaderField(index=6, size=2)
SENDER_HARDWARE = HeaderField(index=8, size=6)
SENDER_PROTOCOL = HeaderField(index=14, size=4)
TARGET_HARDWARE = HeaderField(index=18, size=6)
TARGET_PROTOCOL = HeaderField(index=24, size=4)
