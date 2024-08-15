from fasthtml.common import *
from datetime import time, date
from dataclasses import dataclass, field
from models import Appointment
import math

tailwind = Script(src="/static/tailwind345.js"),
pico = Link(rel="stylesheet", href="/static/pico.min.css"),
increment_decrement_script = Script(src="/static/incr_decr.js")
favicon = Link(type="image/png", size="32x32", rel="icon", href="/static/icons8-zeitplan-sf-black-filled-32.png")

app = FastHTML(hdrs=(tailwind, pico, increment_decrement_script, favicon))
app.mount("/static", StaticFiles(directory="static"), name="static")
rt = app.route


@rt("/")
async def get():
    return Title("Stundenplan"), Main(H1("Stundenplan", cls="text-5xl m-4"), Div(Navigation(), WeekTable(), FoodModal(
        [FoodListing("Asia Noodles", "coming soon"), FoodListing("Rumpsteak", "coming soon too")]
    )), cls="space-y-4")


@rt("/table")
async def post(weeks_from_now: int):
    print(f"Weeks from now: {weeks_from_now}")
    table = WeekTable()
    appointment = Appointment(date = date(2024, 8, 2), start_time = time(8, 5), end_time = time(10), subject = "Mathematik", room = "A123")
    table.register_appointment(appointment)
    appointment2 = Appointment(date = date(2024, 8, 1), start_time = time(8), end_time = time(10), subject = "Deutsch", room = "A123")
    table.register_appointment(appointment2)
    return table


@dataclass
class WeekTable:
    rows: list = field(default_factory=list)
    row_minutes: int = 15
    num_rows: int = 24 * 60 // row_minutes

    def __post_init__(self):
        for i in range(self.num_rows):
            self.rows.append(TableRow(
                start_time = time(hour = (i * self.row_minutes) // 60 % 24, minute = (i * self.row_minutes) % 60),
                end_time = time(hour = ((i + 1) * self.row_minutes) // 60 % 24, minute = ((i + 1) * self.row_minutes) % 60),
                index = i
            ))

    def __ft__(self):
        return Table(
            Tr(Th(Span("Montag"), A(Img(src="/static/icons8-essen-90.png", cls="w-6"), onclick="modal.show()"), cls="flex space-x-2 items-center"), Th("Dienstag"), Th("Mittwoch"), Th("Donnerstag"), Th("Freitag")),
            *[row for row in self.rows if row.used],
            cls="p-4",
            id="stundenplan"
        )

    def register_appointment(self, appointment: Appointment):
        offsets = []
        for row in self.rows:
            offset = abs(time_diff_in_minutes(appointment.start_time, row.start_time))
            offsets.append((offset, row))
        offsets.sort(key=lambda x: x[0])
        for _, row in offsets:
            weekday = appointment.date.weekday()
            if row.entries[weekday] is not None and row.entries[weekday] == Td():
                print(f"Registering appointment {appointment.subject} at {appointment.start_time} in row {row.index}")
                intended_span = math.ceil(time_diff_in_minutes(appointment.end_time, row.start_time) / self.row_minutes)
                actual_span = intended_span
                for i in range(1, int(intended_span)):
                    self.rows[row.index + i].used = True
                    if self.rows[row.index + i].entries[weekday] == Td():
                        self.rows[row.index + i].entries[weekday] = None
                    else:
                        actual_span = i
                        break
                row.entries[weekday] = TableEntry(appointment, rowspan=actual_span)
                row.used = True
                break


@dataclass
class TableRow:
    start_time: time
    end_time: time
    index: int
    entries: list = field(default_factory=lambda: [Td() for _ in range(5)])
    used: bool = False

    def __ft__(self):
        return Tr(*self.entries)


def TableEntry(appointment: Appointment, rowspan=1):
    return Td(
        Div(
            Span(appointment.start_time.strftime("%H:%M"), cls="font-bold"),
            Span(appointment.end_time.strftime(" - %H:%M")),
            Span(appointment.subject, cls="block"),
            Span(appointment.room, cls="block"),
            cls="space-y-1",
        ),
        rowspan=rowspan
    )


class FoodModal:
    def __init__(self, listings: list):
        self.listings = listings
    def __ft__(self):
        return Dialog(
            Form(Div(Div(H2("Speiseplan", cls="text-2xl font-bold"), Button("close", method="close"), cls="flex justify-between items-center"), Div(
                *self.listings,
                cls="grid grid-cols-2 gap-4 mt-4"), cls="bg-black opacity-80 p-6 rounded-lg shadow-lg max-w-2xl w-full"), method="dialog"),
            id="modal",
            cls="fixed inset-0 flex items-center justify-center bg-black bg-opacity-50"
        )

class FoodListing:
    def __init__(self, name: str, img_src: str):
        self.name = name
        self.img_src = img_src

    def __ft__(self):
        return Div(Img(src=self.img_src, alt=self.name, cls="w-full h-48 object-cover rounded-lg"), H3(self.name, cls="text-lg font-semibold mt-2"), cls="text-center")

def Navigation(weeks_from_now=0):
    return Div(
        Button("<", cls="w-6 h-8", onclick="modify_weeks_from_now(-1)"),
        Input(type="number", value=weeks_from_now, id="weeks_from_now", style="width: 4rem; height: 2rem; text-align: center", hx_trigger="change", hx_post="/table", hx_target="#stundenplan", hx_swap="outerHTML", cls="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"),
        Button(">", cls="w-6 h-8", onclick="modify_weeks_from_now(1)"),
        cls="flex justify-center space-x-2"
    )


def time_diff_in_minutes(start: time, end: time):
    return start.hour * 60 + start.minute - end.hour * 60 - end.minute


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

