from fasthtml.common import *
import random
from datetime import datetime

tailwind = Script(src="https://cdn.tailwindcss.com"),
pico = Link(rel="stylesheet", href="https://cdn.jsdelivr.net/npm/@picocss/pico@2/css/pico.min.css"),
increment_decrement_script = Script("""
function increment_weeks_from_now() {
    var weeks = document.getElementById('weeks_from_now');
    weeks.value = parseInt(weeks.value) + 1;
    weeks.dispatchEvent(new Event('change'));
}

function decrement_weeks_from_now() {
    var weeks = document.getElementById('weeks_from_now');
    weeks.value = parseInt(weeks.value) - 1;
    weeks.dispatchEvent(new Event('change'));
}

document.addEventListener('keydown', function(e) {
    if (e.key === 'k' || e.key === 'ArrowLeft') {
        decrement_weeks_from_now();
    } else if (e.key === 'j' || e.key === 'ArrowRight') {
        increment_weeks_from_now();
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
    return WeekTable()


def WeekTable():
    return Table(
        Tr(Th("Montag"), Th("Dienstag"), Th("Mittwoch"), Th("Donnerstag"), Th("Freitag")),
        Tr(random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry()),
        Tr(random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry()),
        Tr(random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry()),
        Tr(random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry(), random_table_entry()),
        cls="p-4",
        id="stundenplan"
    )

def Navigation(weeks_from_now=0):
    return Div(
        Button("<", cls="w-6 h-8", onclick="decrement_weeks_from_now()"),
        Input(type="number", value=weeks_from_now, id="weeks_from_now", style="width: 4rem; height: 2rem; text-align: center", hx_trigger="change", hx_post="/table", hx_target="#stundenplan", hx_swap="outerHTML"),
        Button(">", cls="w-6 h-8", onclick="increment_weeks_from_now()"),
        cls="flex justify-center space-x-2"
    )


def TableEntry(start_time: datetime, end_time: datetime, subject: str, room: str):
    return Td(
        Div(
            Span(start_time.strftime("%H:%M"), cls="font-bold"),
            Span(end_time.strftime(" - %H:%M")),
            Span(subject, cls="block"),
            Span(room, cls="block"),
            cls="space-y-1"
        ),
    )

def random_table_entry():
    start_time = datetime.now().replace(hour=random.randint(8, 16), minute=random.randint(0, 59))
    end_time = start_time.replace(hour=start_time.hour + 1)
    return TableEntry(start_time, end_time, "Security", "A123")

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

