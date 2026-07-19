from flask import Blueprint, render_template, request
from models.wire import Wire

dashboard_bp = Blueprint("dashboard", __name__)

@dashboard_bp.route("/")
def dashboard():

    search = request.args.get("search", "")

    if search:
        wires = Wire.query.filter(
            Wire.multiwire_no.contains(search)
        ).all()
    else:
        wires = Wire.query.order_by(
            Wire.id.desc()
        ).all()

    return render_template(
        "dashboard.html",
        wires=wires,
        search=search
    )