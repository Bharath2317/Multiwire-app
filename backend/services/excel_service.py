import os
from openpyxl import load_workbook

from models.entry import Entry


def generate_excel(wire):

    # Path to template
    BASE_DIR = os.path.dirname(os.path.dirname(__file__))
    TEMPLATE_PATH = os.path.join(
        BASE_DIR,
        "excel",
        "template.xlsx"
    )

    # Load workbook
    workbook = load_workbook(TEMPLATE_PATH)
    sheet = workbook.active

    # Load entries from database
    entries = Entry.query.filter_by(
        wire_id=wire.id
    ).all()

    # Report title
    sheet["B1"] = (
        f"MULTI WIRE {wire.multiwire_no} "
        f"SET PERFORMANCE REPORT"
    )

    row = 8

    for i, e in enumerate(entries, start=1):

        sheet[f"A{row}"] = i
        sheet[f"B{row}"] = e.entry_date
        sheet[f"C{row}"] = e.working_hours
        sheet[f"D{row}"] = e.start_time
        sheet[f"E{row}"] = e.end_time
        sheet[f"F{row}"] = e.block_number
        sheet[f"G{row}"] = e.material
        sheet[f"H{row}"] = e.hardness
        sheet[f"I{row}"] = e.length
        sheet[f"J{row}"] = e.height
        sheet[f"K{row}"] = e.no_of_wires
        sheet[f"L{row}"] = e.down_speed
        sheet[f"M{row}"] = e.peripheral_speed
        sheet[f"N{row}"] = e.tension
        sheet[f"O{row}"] = e.ampere
        sheet[f"P{row}"] = e.remarks

        # Leave one NOTE row between entries
        row += 2

    return workbook