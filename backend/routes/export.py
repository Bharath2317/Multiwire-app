import os
from flask import Blueprint, send_file
from models.wire import Wire
from services.excel_service import generate_excel

export_bp = Blueprint("export", __name__)

@export_bp.route("/export/<int:wire_id>")
def export_excel(wire_id):

    wire = Wire.query.get_or_404(wire_id)

    workbook = generate_excel(wire)

    filename = f"{wire.multiwire_no}.xlsx"

    output_path = os.path.join(
        os.path.dirname(os.path.dirname(__file__)),
        filename
    )

    workbook.save(output_path)

    return send_file(
        output_path,
        as_attachment=True,
        download_name=filename
    )