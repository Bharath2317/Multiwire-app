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

        entry = Entry(
            wire_id=wire.id,
            entry_date=datetime.strptime(
                data["entry_date"],
                "%Y-%m-%d",
            ).date(),
            working_hours=float(data["working_hours"]) if data.get("working_hours") else None,
            start_time=data.get("start_time"),
            end_time=data.get("end_time"),
            block_number=data.get("block_number"),
            length=float(data["length"]) if data.get("length") else None,
            height=float(data["height"]) if data.get("height") else None,
            no_of_wires=int(data["no_of_wires"]) if data.get("no_of_wires") else None,
            material=data.get("material"),
            hardness=data.get("hardness"),
            down_speed=float(data["down_speed"]) if data.get("down_speed") else None,
            peripheral_speed=float(data["peripheral_speed"]) if data.get("peripheral_speed") else None,
            tension=float(data["tension"]) if data.get("tension") else None,
            ampere=float(data["ampere"]) if data.get("ampere") else None,
            remarks=data.get("remarks"),
        )

        db.session.add(entry)
        db.session.commit()

        session.pop("entry_data", None)

        return redirect(url_for("wire.wire_details", id=wire.id))

    return render_template(
        "review_entry.html",
        wire=wire,
        data=data,
    )