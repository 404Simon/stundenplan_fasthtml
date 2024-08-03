from dataclasses import dataclass
from datetime import datetime

@dataclass
class Appointment:
    date: datetime
    start_time: datetime
    end_time: datetime
    subject: str
    room: str

