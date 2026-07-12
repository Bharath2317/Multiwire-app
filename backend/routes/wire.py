from flask import Blueprint, render_template, request, redirect, url_for
from models import db
from models.wire import Wire

wire_bp = Blueprint("wire", __name__)


@wire_bp.route("/new", methods=["GET", "POST"])
def new_wire():

    if request.method == "POST":

        number = request.form.get("multiwire_no")

        wire = Wire(
            multiwire_no=number
        )

        db.session.add(wire)
        db.session.commit()

        return redirect(url_for("dashboard.dashboard"))

    return render_template("new_wire.html")


@wire_bp.route("/wire/<int:id>")
def wire_details(id):

    wire = Wire.query.get_or_404(id)

    return render_template(
        "wire.html",
        wire=wire
    )