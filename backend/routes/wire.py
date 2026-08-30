from flask import Blueprint, render_template, request, redirect, url_for

from models import db
from models.wire import Wire
from models.entry import Entry

wire_bp = Blueprint("wire", __name__)


@wire_bp.route("/wire/<int:id>")
def wire_details(id):

    wire = Wire.query.get_or_404(id)

    entries = Entry.query.filter_by(
        wire_id=id
    ).order_by(
        Entry.entry_date.desc()
    ).all()

    return render_template(
        "wire.html",
        wire=wire,
        entries=entries
    )


@wire_bp.route("/wire/<int:id>/finish", methods=["POST"])
def finish_wire(id):

    wire = Wire.query.get_or_404(id)

    if wire.status == "NEW SET":

        wire.status = "AFTER REPLASTIFICATION"

    elif wire.status == "AFTER REPLASTIFICATION":

        wire.status = "COMPLETED"

    db.session.commit()

    return redirect(
        url_for(
            "wire.wire_details",
            id=id
        )
    )
@wire_bp.route("/new", methods=["GET", "POST"])
def new_wire():

    if request.method == "POST":

        multiwire_no = request.form.get("multiwire_no")

        if not multiwire_no:
            return "Multi Wire Number is required", 400

        wire = Wire(
            multiwire_no=multiwire_no,
            status="NEW SET"
        )

        db.session.add(wire)
        db.session.commit()

        return redirect(
            url_for(
                "wire.wire_details",
                id=wire.id
            )
        )

    return render_template("new_wire.html")