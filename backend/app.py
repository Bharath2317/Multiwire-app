from flask import Flask
from config import Config
from models import db
from models.wire import Wire
from models.entry import Entry
from routes.entry import entry_bp

from routes.dashboard import dashboard_bp
from routes.wire import wire_bp
from routes.export import export_bp


def create_app():

    app = Flask(__name__)

    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():

        from models.wire import Wire

        db.create_all()

    app.register_blueprint(dashboard_bp)
    app.register_blueprint(wire_bp)
    app.register_blueprint(entry_bp)
    app.register_blueprint(export_bp)

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)