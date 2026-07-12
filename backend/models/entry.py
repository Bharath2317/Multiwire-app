from datetime import datetime
from models import db


class Entry(db.Model):
    __tablename__ = "entries"

    id = db.Column(db.Integer, primary_key=True)

    wire_id = db.Column(
        db.Integer,
        db.ForeignKey("wires.id"),
        nullable=False
    )

    entry_date = db.Column(db.Date, nullable=False)

    working_hours = db.Column(db.Float)

    start_time = db.Column(db.String(10))

    end_time = db.Column(db.String(10))

    block_number = db.Column(db.String(50))

    length = db.Column(db.Float)

    height = db.Column(db.Float)

    no_of_wires = db.Column(db.Integer)

    material = db.Column(db.String(100))

    hardness = db.Column(db.String(50))

    down_speed = db.Column(db.Float)

    peripheral_speed = db.Column(db.Float)

    tension = db.Column(db.Float)

    ampere = db.Column(db.Float)

    remarks = db.Column(db.Text)

    stage = db.Column(
        db.String(30),
        default="NEW SET"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )