import re
from io import BytesIO

from flask import Blueprint, send_file

from models import db
from models.wire import Wire
from services.excel_service import generate_excel

export_bp = Blueprint("export", __name__)

XLSX_MIME = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


@export_bp.route("/export/<int:wire_id>")
def export_excel(wire_id):
    wire = db.get_or_404(Wire, wire_id)

    workbook = generate_excel(wire)

    buffer = BytesIO()
    workbook.save(buffer)
    buffer.seek(0)

    safe_name = re.sub(r"[^A-Za-z0-9._-]+", "_", wire.multiwire_no)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{safe_name}.xlsx",
        mimetype=XLSX_MIME,
    )
