from protocols.constants.header_field import HeaderField


ICMP_TYPE = HeaderField(index=0, size=1)
CODE = HeaderField(index=1, size=1)
CHECKSUM = HeaderField(index=2, size=2)
IDENTIFIER = HeaderField(index=4, size=2)
SEQUENCE_NUMBER = HeaderField(index=6, size=2)
TIMESTAMP = HeaderField(index=8, size=8)
DATA = HeaderField(index=16, size=48)

REQUEST_TYPE = 8
REPLY_TYPE = 0
