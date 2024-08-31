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

@dataclass
class SpeiseplanDay:
    date: date
    title: str
    price: str
    img: str|None


class TableEntryState(Enum):
    EMPTY = 0
    FILLED = 1
    SPANNED = 2

