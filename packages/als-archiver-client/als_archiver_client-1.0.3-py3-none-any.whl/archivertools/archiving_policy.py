from enum import Enum

class ArchivingPolicy(Enum):
    VERYSLOW = 0
    SLOW = 1
    MEDIUM = 2
    FAST = 3
    VERYFAST = 4

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented