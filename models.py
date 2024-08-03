from dataclasses import dataclass
from datetime import time, date

@dataclass
class Appointment:
    date: date
    start_time: time
    end_time: time
    subject: str
    room: str

