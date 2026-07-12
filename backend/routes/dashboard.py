from flask import Blueprint, render_template
from models.wire import Wire

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/")
def dashboard():
    wires = Wire.query.order_by(Wire.created_at.desc()).all()
    return render_template("dashboard.html", wires=wires)