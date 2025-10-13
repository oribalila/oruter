from dataclasses import dataclass


@dataclass
class HeaderField:
    """This class represents a field in a general networking header,
    specifying its index in the header (in bytes) and size in bytes.
    """

    index: int
    size: int

    def __len__(self):
        return self.size
