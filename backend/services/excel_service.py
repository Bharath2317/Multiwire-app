import os
from openpyxl import load_workbook

from models.entry import Entry

# Rows available in the Excel template (one entry every 2 rows)
NEW_SET_CAPACITY = 32      # rows 8..70
REPLAST_CAPACITY = 22      # rows 75..117


def generate_excel(wire):

    # --------------------------------
    # Find Excel template
    # --------------------------------

    BASE_DIR = os.path.dirname(os.path.dirname(__file__))

    TEMPLATE_PATH = os.path.join(
        BASE_DIR,
        "excel",
        "template.xlsx"
    )

    # --------------------------------
    # Load template
    # --------------------------------

    workbook = load_workbook(TEMPLATE_PATH)

    sheet = workbook.active

    # --------------------------------
    # Get entries from database
    # --------------------------------

    entries = Entry.query.filter_by(
        wire_id=wire.id
    ).order_by(
        Entry.entry_date
    ).all()

    # --------------------------------
    # Report title
    # --------------------------------

    sheet["B1"] = (
        f"MULTI WIRE {wire.multiwire_no} "
        f"SET PERFORMANCE REPORT"
    )

    # --------------------------------
    # NEW SET
    # --------------------------------

    new_set_row = 8
    new_set_number = 1

    # Maximum NEW SET rows:
    # 8,10,12,...,70

    for entry in entries:

        if getattr(entry, "stage", "NEW SET") != "NEW SET":
            continue

        if new_set_row > 70:
            break

        write_entry(
            sheet,
            new_set_row,
            new_set_number,
            entry
        )

        new_set_number += 1
        new_set_row += 2

    # --------------------------------
    # AFTER REPLASTIFICATION
    # --------------------------------

    replast_row = 75
    replast_number = 1

    for entry in entries:

        if getattr(entry, "stage", "") != "AFTER REPLASTIFICATION":
            continue

        if replast_row > 117:
            break

        write_entry(
            sheet,
            replast_row,
            replast_number,
            entry
        )

        replast_number += 1
        replast_row += 2

    # --------------------------------
    # Keep SQMT formulas
    # --------------------------------

    sheet["S72"] = "=SUM(S8:S70)"
    sheet["S119"] = "=SUM(S75:S117)"

    sheet["K3"] = "=S72"
    sheet["K4"] = "=S119"
    sheet["K5"] = "=SUM(K3:K4)"

    return workbook


def write_entry(sheet, row, serial_no, entry):

    # Serial number
    sheet[f"A{row}"] = serial_no

    # Date
    sheet[f"B{row}"] = entry.entry_date

    # Working hours
    sheet[f"C{row}"] = entry.working_hours

    # Start time
    sheet[f"D{row}"] = entry.start_time

    # End time
    sheet[f"E{row}"] = entry.end_time

    # Block number
    sheet[f"F{row}"] = entry.block_number

    # Material
    sheet[f"G{row}"] = entry.material

    # Hardness
    sheet[f"H{row}"] = entry.hardness

    # Length
    sheet[f"I{row}"] = entry.length

    # Height
    sheet[f"J{row}"] = entry.height

    # Number of wires
    sheet[f"K{row}"] = entry.no_of_wires

    # Down speed
    sheet[f"L{row}"] = entry.down_speed

    # Peripheral speed
    sheet[f"M{row}"] = entry.peripheral_speed

    # Tension
    sheet[f"N{row}"] = entry.tension

    # Bead diameter
    sheet[f"O{row}"] = entry.bead_diameter

    # Ampere
    sheet[f"P{row}"] = entry.ampere

    # Broken wire code
    sheet[f"Q{row}"] = entry.broken_wire_code

    # SQMT
    sheet[f"S{row}"] = (
        f"=(I{row}*J{row}/10000)*K{row}"
    )