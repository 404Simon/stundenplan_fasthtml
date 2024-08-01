from fasthtml.common import *
import random

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
""")

app = FastHTML(hdrs=(tailwind, pico, increment_decrement_script))
rt = app.route


@rt("/")
async def get():
    return Title("Stundenplan"), Main(H1("Stundenplan", cls="text-5xl m-4"), WeekTable())

@rt("/table")
async def post(weeks_from_now: int):
    print(f"Weeks from now: {weeks_from_now}")
    return WeekTable(weeks_from_now)

def render_table():
    return Table(
        Tr(Th("Montag"), Th("Dienstag"), Th("Mittwoch"), Th("Donnerstag"), Th("Freitag")),
        Tr(Td(random.randint(1,12)), Td("2"), Td("3"), Td("4"), Td("5")),
        Tr(Td("6"), Td("7"), Td("8"), Td("9"), Td("10")),
        Tr(Td("11"), Td("12"), Td("13"), Td("14"), Td("15")),
        Tr(Td("16"), Td("17"), Td("18"), Td("19"), Td("20")),
        cls="m-4"
    )

def Navigation(weeks_from_now=0):
    return Div(
        Button("<", cls="w-6 h-8", onclick="decrement_weeks_from_now()"),
        Input(type="number", value=weeks_from_now, id="weeks_from_now", style="width: 4rem; height: 2rem; text-align: center", hx_trigger="change", hx_post="/table", hx_target="#stundenplan"),
        Button(">", cls="w-6 h-8", onclick="increment_weeks_from_now()"),
        cls="flex justify-center space-x-2"
    )

def WeekTable(weeks_from_now=0):
    return Div(
        Navigation(weeks_from_now),
        render_table(),
        cls="space-y-4",
        id="stundenplan"
    )

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

