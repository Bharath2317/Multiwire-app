from flask import Blueprint, flash, redirect, render_template, request, url_for
from sqlalchemy.exc import IntegrityError

from models import db
from models.entry import Entry
from models.wire import Wire
from services.excel_service import NEW_SET_CAPACITY, REPLAST_CAPACITY

wire_bp = Blueprint("wire", __name__)

STAGES = ["NEW SET", "AFTER REPLASTIFICATION", "COMPLETED"]


def _stage_summary(entries):
    hours = sum(e.working_hours or 0 for e in entries)
    sqmt = sum(
        ((e.length or 0) * (e.height or 0) / 10000) * (e.no_of_wires or 0)
        for e in entries
    )
    return {"count": len(entries), "hours": hours, "sqmt": sqmt}


@wire_bp.route("/wire/<int:id>")
def wire_details(id):
    wire = db.get_or_404(Wire, id)

    entries = (
        Entry.query.filter_by(wire_id=id).order_by(Entry.entry_date.desc()).all()
    )
    new_set = [e for e in entries if e.stage == "NEW SET"]
    replast = [e for e in entries if e.stage == "AFTER REPLASTIFICATION"]

    return render_template(
        "wire.html",
        wire=wire,
        new_set=new_set,
        replast=replast,
        new_summary=_stage_summary(new_set),
        replast_summary=_stage_summary(replast),
        total_summary=_stage_summary(entries),
        new_capacity=NEW_SET_CAPACITY,
        replast_capacity=REPLAST_CAPACITY,
        stage_index=STAGES.index(wire.status) if wire.status in STAGES else 0,
    )


@wire_bp.route("/wire/<int:id>/finish", methods=["POST"])
def finish_wire(id):
    wire = db.get_or_404(Wire, id)

    if wire.status == "NEW SET":
        wire.status = "AFTER REPLASTIFICATION"
    elif wire.status == "AFTER REPLASTIFICATION":
        wire.status = "COMPLETED"

    db.session.commit()
    flash(f"Status is now {wire.status.title()}.", "success")
    return redirect(url_for("wire.wire_details", id=id))


@wire_bp.route("/new", methods=["GET", "POST"])
def new_wire():
    if request.method == "POST":
        multiwire_no = (request.form.get("multiwire_no") or "").strip()

        if not multiwire_no:
            flash("Multi Wire number is required.", "danger")
            return render_template("new_wire.html"), 400

        wire = Wire(multiwire_no=multiwire_no, status="NEW SET")
        db.session.add(wire)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            flash(f"Multi Wire {multiwire_no} already exists.", "danger")
            return render_template("new_wire.html", value=multiwire_no), 409

        flash("Multi Wire created.", "success")
        return redirect(url_for("wire.wire_details", id=wire.id))

    return render_template("new_wire.html")
