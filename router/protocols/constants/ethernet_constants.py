from protocols.constants.header_field import HeaderField


DESTINATION = HeaderField(index=0, size=6)
SOURCE = HeaderField(index=6, size=6)
ETHER_TYPE = HeaderField(index=12, size=2)
