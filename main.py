from fasthtml.common import *

app, rt = fast_app()


@rt("/")
async def get():
    return Title("Stundenplan"), Main(H1("Stundenplan"), get_week_table())

def get_week_table():
    return Table(
        Tr(Th("Montag"), Th("Dienstag"), Th("Mittwoch"), Th("Donnerstag"), Th("Freitag")),
        Tr(Td("1"), Td("2"), Td("3"), Td("4"), Td("5")),
        Tr(Td("6"), Td("7"), Td("8"), Td("9"), Td("10")),
        Tr(Td("11"), Td("12"), Td("13"), Td("14"), Td("15")),
        Tr(Td("16"), Td("17"), Td("18"), Td("19"), Td("20")),
    )

serve()

