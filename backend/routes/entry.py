from flask import Blueprint, render_template, request, redirect, url_for, session
from datetime import date, datetime

from models import db
from models.wire import Wire
from models.entry import Entry

entry_bp = Blueprint("entry", __name__)

FIELDS = [
    ("entry_date", "Date", "date"),
    ("working_hours", "Working Hours", "number"),
    ("start_time", "Start Time", "time"),
    ("end_time", "End Time", "time"),
    ("block_number", "Block Number", "text"),
    ("length", "Length", "number"),
    ("height", "Height", "number"),
    ("no_of_wires", "No Of Wires", "number"),
    ("material", "Material", "text"),
    ("hardness", "Hardness", "text"),
    ("down_speed", "Down Speed", "number"),
    ("peripheral_speed", "Peripheral Speed", "number"),
    ("tension", "Tension", "number"),
    ("ampere", "Ampere", "number"),
    ("remarks", "Remarks", "textarea"),
]


@entry_bp.route("/entry/<int:wire_id>/step/<int:step>", methods=["GET", "POST"])
def entry_step(wire_id, step):

    wire = Wire.query.get_or_404(wire_id)

    if "entry_data" not in session:
        session["entry_data"] = {}

    data = session["entry_data"]

    field_name, field_label, field_type = FIELDS[step]

    if request.method == "POST":

        data[field_name] = request.form.get(field_name)

        session["entry_data"] = data

        if step == len(FIELDS) - 1:
            return redirect(url_for("entry.review_entry", wire_id=wire.id))

        return redirect(
            url_for(
                "entry.entry_step",
                wire_id=wire.id,
                step=step + 1,
            )
        )

    return render_template(
        "entry_step.html",
        wire=wire,
        field_name=field_name,
        field_label=field_label,
        field_type=field_type,
        value=data.get(field_name, ""),
        step=step,
        total=len(FIELDS),
        today=date.today().isoformat(),
    )


@entry_bp.route("/entry/<int:wire_id>/review", methods=["GET", "POST"])
def review_entry(wire_id):

    wire = Wire.query.get_or_404(wire_id)

    data = session.get("entry_data", {})

    if request.method == "POST":

        data = session["entry_data"]

        if "edit_entry_id" in session:
            entry = Entry.query.get(session["edit_entry_id"])
        else:
            entry = Entry(wire_id=wire.id)

        entry.entry_date = datetime.strptime(
            data["entry_date"],
            "%Y-%m-%d"
        ).date()

        entry.working_hours = float(data["working_hours"]) if data.get("working_hours") else None
        entry.start_time = data.get("start_time")
        entry.end_time = data.get("end_time")
        entry.block_number = data.get("block_number")
        entry.length = float(data["length"]) if data.get("length") else None
        entry.height = float(data["height"]) if data.get("height") else None
        entry.no_of_wires = int(data["no_of_wires"]) if data.get("no_of_wires") else None
        entry.material = data.get("material")
        entry.hardness = data.get("hardness")
        entry.down_speed = float(data["down_speed"]) if data.get("down_speed") else None
        entry.peripheral_speed = float(data["peripheral_speed"]) if data.get("peripheral_speed") else None
        entry.tension = float(data["tension"]) if data.get("tension") else None
        entry.ampere = float(data["ampere"]) if data.get("ampere") else None
        entry.remarks = data.get("remarks")

        if "edit_entry_id" not in session:
            db.session.add(entry)
            
        entry.stage = wire.status
        db.session.commit()

        session.pop("entry_data", None)
        session.pop("edit_entry_id", None)

        return redirect(
            url_for(
                "wire.wire_details",
                id=wire.id
            )
        )

    return render_template(
        "review_entry.html",
        wire=wire,
        data=data
    )

@entry_bp.route("/entry/edit/<int:id>")
@entry_bp.route("/entry/edit/<int:id>", methods=["GET"])
def edit_entry(id):

    entry = Entry.query.get_or_404(id)

    session["entry_data"] = {
        "entry_date": entry.entry_date.strftime("%Y-%m-%d") if entry.entry_date else "",
        "working_hours": entry.working_hours,
        "start_time": entry.start_time,
        "end_time": entry.end_time,
        "block_number": entry.block_number,
        "length": entry.length,
        "height": entry.height,
        "no_of_wires": entry.no_of_wires,
        "material": entry.material,
        "hardness": entry.hardness,
        "down_speed": entry.down_speed,
        "peripheral_speed": entry.peripheral_speed,
        "tension": entry.tension,
        "ampere": entry.ampere,
        "remarks": entry.remarks,
    }

    session["edit_entry_id"] = entry.id

    return redirect(
        url_for(
            "entry.entry_step",
            wire_id=entry.wire_id,
            step=0
        )
    )