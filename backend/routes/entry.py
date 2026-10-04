from datetime import date, datetime

from flask import (
    Blueprint,
    abort,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from models import db
from models.entry import Entry
from models.wire import Wire

entry_bp = Blueprint("entry", __name__)

# (field name, label, input type, required, hint)
FIELDS = [
    ("entry_date", "Date", "date", True, ""),
    ("working_hours", "Working Hours", "number", True, "e.g. 7.5"),
    ("start_time", "Start Time", "time", False, ""),
    ("end_time", "End Time", "time", False, ""),
    ("block_number", "Block Number", "text", False, ""),
    ("length", "Length", "number", False, "cm"),
    ("height", "Height", "number", False, "cm"),
    ("no_of_wires", "No Of Wires", "number", False, ""),
    ("material", "Material", "text", False, ""),
    ("hardness", "Hardness", "text", False, ""),
    ("down_speed", "Down Speed", "number", False, ""),
    ("peripheral_speed", "Peripheral Speed", "number", False, ""),
    ("tension", "Tension", "number", False, ""),
    ("ampere", "Ampere", "number", False, ""),
    ("bead_diameter", "Bead Diameter", "number", False, ""),
    ("broken_wire_code", "Broken Wire Code", "text", False, "leave empty if none"),
    ("remarks", "Remarks", "textarea", False, ""),
]

FLOAT_FIELDS = {
    "working_hours", "length", "height", "down_speed",
    "peripheral_speed", "tension", "ampere", "bead_diameter",
}
INT_FIELDS = {"no_of_wires"}
NON_NEGATIVE = FLOAT_FIELDS | INT_FIELDS


def _reset_draft():
    for key in ("entry_data", "edit_entry_id", "entry_wire_id"):
        session.pop(key, None)


def _draft_for(wire_id):
    """Return the in-progress draft, discarding it if it belongs to another wire."""
    if session.get("entry_wire_id") != wire_id:
        _reset_draft()
        session["entry_wire_id"] = wire_id
        session["entry_data"] = {}
    return session["entry_data"]


@entry_bp.route("/entry/<int:wire_id>/new")
def new_entry(wire_id):
    """Always start a fresh entry (clears any half-finished edit)."""
    Wire.query.get_or_404(wire_id)
    _reset_draft()
    session["entry_wire_id"] = wire_id
    session["entry_data"] = {}
    return redirect(url_for("entry.entry_step", wire_id=wire_id, step=0))


COPY_FIELDS = [
    "block_number", "length", "height", "no_of_wires", "material", "hardness",
    "down_speed", "peripheral_speed", "tension", "ampere", "bead_diameter",
]


@entry_bp.route("/entry/<int:wire_id>/copy-last")
def copy_last_entry(wire_id):
    """Start a new entry pre-filled from the most recent entry of this wire.

    Date, hours, times, broken wire code and remarks are left blank because
    they differ every day.
    """
    Wire.query.get_or_404(wire_id)
    last = (
        Entry.query.filter_by(wire_id=wire_id)
        .order_by(Entry.entry_date.desc(), Entry.id.desc())
        .first()
    )
    if last is None:
        flash("There is no previous entry to copy.", "warning")
        return redirect(url_for("wire.wire_details", id=wire_id))

    _reset_draft()
    session["entry_wire_id"] = wire_id
    session["entry_data"] = {
        name: ("" if getattr(last, name) is None else getattr(last, name))
        for name in COPY_FIELDS
    }
    flash("Copied from the last entry. Review each step and change what differs.", "info")
    return redirect(url_for("entry.entry_step", wire_id=wire_id, step=0))


@entry_bp.route("/entry/<int:wire_id>/step/<int:step>", methods=["GET", "POST"])
def entry_step(wire_id, step):
    wire = db.get_or_404(Wire, wire_id)

    if step >= len(FIELDS):
        abort(404)

    data = _draft_for(wire_id)
    field_name, field_label, field_type, required, hint = FIELDS[step]

    if request.method == "POST":
        raw = (request.form.get(field_name) or "").strip()

        if required and not raw:
            flash(f"{field_label} is required.", "danger")
            return redirect(url_for("entry.entry_step", wire_id=wire_id, step=step))

        if field_name == "working_hours" and raw:
            try:
                hours = float(raw)
            except ValueError:
                hours = None
            if hours is not None and not 0 < hours <= 24:
                flash("Working hours must be between 0 and 24.", "danger")
                return redirect(
                    url_for("entry.entry_step", wire_id=wire_id, step=step)
                )

        if raw and field_name in NON_NEGATIVE:
            try:
                number = float(raw)
            except ValueError:
                flash(f"{field_label} must be a number.", "danger")
                return redirect(
                    url_for("entry.entry_step", wire_id=wire_id, step=step)
                )
            if number < 0:
                flash(f"{field_label} cannot be negative.", "danger")
                return redirect(
                    url_for("entry.entry_step", wire_id=wire_id, step=step)
                )

        data[field_name] = raw
        session["entry_data"] = data

        if step == len(FIELDS) - 1:
            return redirect(url_for("entry.review_entry", wire_id=wire.id))

        return redirect(
            url_for("entry.entry_step", wire_id=wire.id, step=step + 1)
        )

    return render_template(
        "entry_step.html",
        wire=wire,
        field_name=field_name,
        field_label=field_label,
        field_type=field_type,
        required=required,
        hint=hint,
        value="" if data.get(field_name) is None else data.get(field_name),
        step=step,
        total=len(FIELDS),
        today=date.today().isoformat(),
        step_decimal=(field_type == "number"),
        editing="edit_entry_id" in session,
    )


@entry_bp.route("/entry/<int:wire_id>/review", methods=["GET", "POST"])
def review_entry(wire_id):
    wire = db.get_or_404(Wire, wire_id)

    data = session.get("entry_data", {})
    if session.get("entry_wire_id") != wire_id or not data.get("entry_date"):
        flash("Start a new entry first.", "warning")
        return redirect(url_for("wire.wire_details", id=wire_id))

    if request.method == "POST":
        edit_id = session.get("edit_entry_id")

        if edit_id:
            entry = db.session.get(Entry, edit_id)
            if entry is None or entry.wire_id != wire.id:
                abort(404)
        else:
            entry = Entry(wire_id=wire.id, stage=wire.status)

        try:
            entry.entry_date = datetime.strptime(
                data["entry_date"], "%Y-%m-%d"
            ).date()
            for name in FLOAT_FIELDS:
                setattr(entry, name, float(data[name]) if data.get(name) else None)
            for name in INT_FIELDS:
                setattr(entry, name, int(float(data[name])) if data.get(name) else None)
        except (ValueError, KeyError):
            flash("Some values are invalid. Please check the entry.", "danger")
            return redirect(url_for("entry.entry_step", wire_id=wire.id, step=0))

        entry.start_time = data.get("start_time") or None
        entry.end_time = data.get("end_time") or None
        entry.block_number = data.get("block_number") or None
        entry.material = data.get("material") or None
        entry.hardness = data.get("hardness") or None
        entry.broken_wire_code = data.get("broken_wire_code") or None
        entry.remarks = data.get("remarks") or None

        if not edit_id:
            db.session.add(entry)
        db.session.commit()

        _reset_draft()
        flash("Entry saved.", "success")
        return redirect(url_for("wire.wire_details", id=wire.id))

    rows = [
        (label, data.get(name, ""))
        for name, label, _type, _req, _hint in FIELDS
    ]
    return render_template(
        "review_entry.html",
        wire=wire,
        rows=rows,
        editing="edit_entry_id" in session,
    )


@entry_bp.route("/entry/edit/<int:id>")
def edit_entry(id):
    entry = db.get_or_404(Entry, id)

    def fmt(value):
        return "" if value is None else value

    _reset_draft()
    session["entry_wire_id"] = entry.wire_id
    session["entry_data"] = {
        "entry_date": entry.entry_date.strftime("%Y-%m-%d") if entry.entry_date else "",
        "working_hours": fmt(entry.working_hours),
        "start_time": fmt(entry.start_time),
        "end_time": fmt(entry.end_time),
        "block_number": fmt(entry.block_number),
        "length": fmt(entry.length),
        "height": fmt(entry.height),
        "no_of_wires": fmt(entry.no_of_wires),
        "material": fmt(entry.material),
        "hardness": fmt(entry.hardness),
        "down_speed": fmt(entry.down_speed),
        "peripheral_speed": fmt(entry.peripheral_speed),
        "tension": fmt(entry.tension),
        "ampere": fmt(entry.ampere),
        "bead_diameter": fmt(entry.bead_diameter),
        "broken_wire_code": fmt(entry.broken_wire_code),
        "remarks": fmt(entry.remarks),
    }
    session["edit_entry_id"] = entry.id

    return redirect(url_for("entry.entry_step", wire_id=entry.wire_id, step=0))


@entry_bp.route("/entry/delete/<int:id>", methods=["POST"])
def delete_entry(id):
    entry = db.get_or_404(Entry, id)
    wire_id = entry.wire_id
    db.session.delete(entry)
    db.session.commit()
    flash("Entry deleted.", "success")
    return redirect(url_for("wire.wire_details", id=wire_id))
