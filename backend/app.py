import os

from flask import Flask
from sqlalchemy import inspect, text

from config import Config
from models import db
from models.wire import Wire  # noqa: F401  (registers the table)
from models.entry import Entry  # noqa: F401
from routes.entry import entry_bp
from routes.dashboard import dashboard_bp
from routes.wire import wire_bp
from routes.export import export_bp


NEW_ENTRY_COLUMNS = {
    "bead_diameter": "FLOAT",
    "broken_wire_code": "VARCHAR(50)",
}


def ensure_entry_columns():
    """create_all() never alters existing tables, so add new columns here."""
    existing = {c["name"] for c in inspect(db.engine).get_columns("entries")}
    with db.engine.begin() as conn:
        for name, ddl in NEW_ENTRY_COLUMNS.items():
            if name not in existing:
                conn.execute(text(f"ALTER TABLE entries ADD {name} {ddl} NULL"))


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()
        ensure_entry_columns()

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(wire_bp)
    app.register_blueprint(entry_bp)
    app.register_blueprint(export_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=os.getenv("FLASK_DEBUG", "1") == "1")
