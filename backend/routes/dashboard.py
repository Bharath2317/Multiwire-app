from flask import Blueprint, render_template, request

from models.wire import Wire

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    search = request.args.get("search", "").strip()

    query = Wire.query
    if search:
        query = query.filter(Wire.multiwire_no.contains(search))
    wires = query.order_by(Wire.id.desc()).all()

    counts = {
        "total": Wire.query.count(),
        "new": Wire.query.filter_by(status="NEW SET").count(),
        "replast": Wire.query.filter_by(status="AFTER REPLASTIFICATION").count(),
        "done": Wire.query.filter_by(status="COMPLETED").count(),
    }

    return render_template(
        "dashboard.html", wires=wires, search=search, counts=counts
    )
