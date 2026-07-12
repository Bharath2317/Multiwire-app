from datetime import datetime
from models import db


class Wire(db.Model):
    __tablename__ = "wires"

    id = db.Column(db.Integer, primary_key=True)

    multiwire_no = db.Column(db.String(50), unique=True, nullable=False)

    status = db.Column(db.String(30), nullable=False, default="NEW SET")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
    )
    entries = db.relationship(
    "Entry",
    backref="wire",
    lazy=True,
    cascade="all, delete-orphan"
)