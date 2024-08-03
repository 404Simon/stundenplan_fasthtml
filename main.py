from fasthtml.common import *
from datetime import time, date
from dataclasses import dataclass, field
from models import Appointment

tailwind = Script(src="https://cdn.tailwindcss.com"),
pico = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
increment_decrement_script = Script("""
function modify_weeks_from_now(value) {
    var weeks = document.getElementById('weeks_from_now');
    if (weeks.value == "") {
        weeks.value = 0;
        weeks.blur();
    }
    weeks.value = parseInt(weeks.value) + value;
    weeks.dispatchEvent(new Event('change'));
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'k' || e.key === 'ArrowLeft') {
        modify_weeks_from_now(-1);
    } else if (e.key === 'j' || e.key === 'ArrowRight') {
        modify_weeks_from_now(1);
    } else if (e.key === ":") {
        var weeks = document.getElementById('weeks_from_now');
        weeks.focus();
        weeks.select();
    }
});
""")

app = FastHTML(hdrs=(tailwind, pico, increment_decrement_script))
rt = app.route


@rt("/")
async def get():
    return Title("Stundenplan"), Main(H1("Stundenplan", cls="text-5xl m-4"), Div(Navigation(), WeekTable()), cls="space-y-4")

@rt("/table")
async def post(weeks_from_now: int):
    print(f"Weeks from now: {weeks_from_now}")
    table = WeekTable()
    appointment = Appointment(date = date(2024, 8, 2), start_time = time(8), end_time = time(10), subject = "Mathematik", room = "A123")
    table.register_appointment(appointment)
    appointment2 = Appointment(date = date(2024, 8, 2), start_time = time(8), end_time = time(10), subject = "Deutsch", room = "A123")
    table.register_appointment(appointment2)
    return table


@dataclass
class WeekTable:
    rows: list = field(default_factory=list)
    row_minutes: int = 30
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
            Tr(Th("Montag"), Th("Dienstag"), Th("Mittwoch"), Th("Donnerstag"), Th("Freitag")),
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
                intended_span = time_diff_in_minutes(appointment.end_time, appointment.start_time) // self.row_minutes
                actual_span = intended_span
                for i in range(1, int(intended_span)):
                    self.rows[row.index + i].used = True
                    if self.rows[row.index + i].entries[weekday] == Td():
                        self.rows[row.index + i].entries[weekday] = None
                    else:
                        actual_span = i
                        break
                row.entries[weekday] = TableEntry(appointment.start_time, appointment.end_time, appointment.subject, appointment.room, rowspan=actual_span)
                row.used = True
                break


def Navigation(weeks_from_now=0):
    return Div(
        Button("<", cls="w-6 h-8", onclick="modify_weeks_from_now(-1)"),
        Input(type="number", value=weeks_from_now, id="weeks_from_now", style="width: 4rem; height: 2rem; text-align: center", hx_trigger="change", hx_post="/table", hx_target="#stundenplan", hx_swap="outerHTML", cls="[appearance:textfield] [&::-webkit-outer-spin-button]:appearance-none [&::-webkit-inner-spin-button]:appearance-none"),
        Button(">", cls="w-6 h-8", onclick="modify_weeks_from_now(1)"),
        cls="flex justify-center space-x-2"
    )


def TableEntry(start_time: time, end_time: time, subject: str, room: str, rowspan=1):
    return Td(
        Div(
            Span(start_time.strftime("%H:%M"), cls="font-bold"),
            Span(end_time.strftime(" - %H:%M")),
            Span(subject, cls="block"),
            Span(room, cls="block"),
            cls="space-y-1",
        ),
        rowspan=rowspan
    )


@dataclass
class TableRow:
    start_time: time
    end_time: time
    index: int
    entries: list = field(default_factory=lambda: [Td() for _ in range(5)])
    used: bool = False

    def __ft__(self):
        return Tr(*self.entries)


def time_diff_in_minutes(start: time, end: time):
    return start.hour * 60 + start.minute - end.hour * 60 - end.minute

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

