from dataclasses import dataclass
from datetime import time, date
from enum import Enum

@dataclass
class Appointment:
    date: date
    start_time: time
    end_time: time
    subject: str
    room: str


class TableEntryState(Enum):
    EMPTY = 0
    FILLED = 1
    SPANNED = 2

