from enum import Enum, auto


class States(Enum):
    CHOOSING = auto()
    WEEKLY_SHIFTS = auto()
    CHOOSE_SHIFT = auto()
    CHANGE_SHIFT = auto()
