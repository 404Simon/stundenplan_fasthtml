import os
from fasthtml.common import *
from datetime import time, date, datetime, timedelta
from dataclasses import dataclass, field
from models import Appointment, TableEntryState
import math
from dualis import Dualis
from functools import lru_cache


dualis = Dualis(os.environ.get("DUALIS_USER"), os.environ.get("DUALIS_PASSWORD"))


tailwind = Script(src="/static/tailwind345.js"),
pico = Link(rel="stylesheet", href="/static/pico.min.css"),
increment_decrement_script = Script(src="/static/incr_decr.js")
favicon = Link(type="image/png", size="32x32", rel="icon", href="/static/icons8-zeitplan-sf-black-filled-32.png")

app = FastHTML(hdrs=(tailwind, pico, increment_decrement_script, favicon))
app.mount("/static", StaticFiles(directory="static"), name="static")
rt = app.route


@rt("/")
async def get():
    return Title("Stundenplan"), Main(H1("Stundenplan", cls="text-5xl m-4"), Div(Navigation(), WeekTable(monday = date.today() - timedelta(days=date.today().weekday()))), cls="space-y-4")


@rt("/table")
async def post(weeks_from_now: int):
    print(f"Weeks from now: {weeks_from_now}")
    monday = date.today() - timedelta(days=date.today().weekday()) + timedelta(weeks=weeks_from_now)
    table = WeekTable(monday = monday)
    return table


@rt("/food")
async def get(date_str: str):
    date = datetime.strptime(date_str, "%Y-%m-%d").date()
    dummy_listings = [FoodListing("Asia Noodles", "http://coming.soon"), FoodListing("Rumpsteak", "http://comming.soon")]
    return FoodModal(date, dummy_listings)


@dataclass
class WeekTable:
    monday: date
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


        appointments = cached_get_time_table_week(self.monday)
        for appointment in appointments:
            self.register_appointment(appointment)


    def __ft__(self):
        days = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        return Div(Table(
            Tr(
                *[Th(
                    Div(
                        Span(day),
                        A(Img(src="/static/icons8-essen-90-inverted.png", cls="w-6"), onclick=f"modal{weekday}.show()"),
                        cls="flex space-x-2 items-center"
                    ),
                    Span((self.monday + timedelta(days=weekday)).strftime("%d.%m"), cls="italic text-sm"),
                    cls="w-1/5"
                ) for weekday, day in enumerate(days)]
            ),
            *[row for row in self.rows if row.used],
            cls="p-4",
        ),
            LazyFoodLoader(self.monday),
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
            if row.entries[weekday].state == TableEntryState.EMPTY:
                row.entries[weekday].state = TableEntryState.FILLED
                intended_span = math.ceil(time_diff_in_minutes(appointment.end_time, row.start_time) / self.row_minutes)
                actual_span = intended_span
                for i in range(1, int(intended_span)):
                    self.rows[row.index + i].used = True
                    if self.rows[row.index + i].entries[weekday].state == TableEntryState.EMPTY:
                        self.rows[row.index + i].entries[weekday].state = TableEntryState.SPANNED
                    else:
                        actual_span = i
                        break
                row.entries[weekday].appointment = appointment
                row.entries[weekday].rowspan = actual_span
                row.used = True
                print(f"Registering appointment {appointment.subject} at {appointment.start_time} in row {row.index} with span {actual_span}")
                break


@dataclass
class TableRow:
    start_time: time
    end_time: time
    index: int
    entries: list = field(default_factory=lambda: [TableEntry() for _ in range(5)])
    used: bool = False

    def __ft__(self):
        return Tr(*self.entries)


@dataclass
class TableEntry:
    appointment: Union[Appointment, None] = None
    rowspan: int = 1
    state: TableEntryState = TableEntryState.EMPTY

    def __ft__(self):
        if self.state == TableEntryState.FILLED and self.appointment:
            return Td(
                Div(
                    Span(self.appointment.start_time.strftime("%H:%M")),
                    Span(self.appointment.end_time.strftime(" - %H:%M")),
                    Span(self.appointment.subject, cls="block text-lg"),
                    Span(self.appointment.room, cls="block"),
                    cls="space-y-4",
                ),
                rowspan=self.rowspan
            )
        elif self.state == TableEntryState.SPANNED:
            return None
        else:
            return Td()



class FoodModal:
    def __init__(self, date: date, listings: list):
        self.date = date
        self.listings = listings
    def __ft__(self):
        return Dialog(Form(
                Div(
                    Div(
                        H2("Speiseplan", cls="text-2xl font-bold"),
                        Button(Div("+", cls="transform rotate-45 translate-x-[1px]"), cls="w-8 h-8 flex items-center justify-center rounded-full border-2 border-white text-white shadow-none hover:bg-white hover:text-black", method="close"),
                        cls="flex justify-between items-center"),
                    Div(
                *self.listings,
                cls="grid grid-cols-2 gap-4 mt-4"), cls="bg-black opacity-80 p-6 rounded-lg shadow-lg max-w-2xl w-full"), method="dialog"),
            id=f"modal{self.date.weekday()}",
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


def LazyFoodLoader(date: date):
    return Div(
            *[Div(
                hx_get=f"/food?date_str={date.strftime('%Y-%m-%d')}",
                hx_swap="outerHTML",
                hx_trigger="load",
                cls="hidden",
            )
                for date in [date + timedelta(days=i) for i in range(5)]
            ]
        )


def time_diff_in_minutes(start: time, end: time):
    return start.hour * 60 + start.minute - end.hour * 60 - end.minute


@lru_cache(maxsize=32)
def cached_get_time_table_week(date: date):
    return dualis.get_time_table_week(date)


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

