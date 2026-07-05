from flask import Flask, render_template, request, redirect, url_for
from config import Config
from models import db
from models.wire import Wire


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    db.init_app(app)

    with app.app_context():
        db.create_all()

    @app.route("/")
    def dashboard():
        wires = Wire.query.order_by(Wire.created_at.desc()).all()
        return render_template("dashboard.html", wires=wires)

    @app.route("/new", methods=["GET", "POST"])
    def new_wire():

        if request.method == "POST":

            number = request.form["multiwire_no"]

            wire = Wire(
                multiwire_no=number
            )

            db.session.add(wire)
            db.session.commit()

            return redirect(url_for("dashboard"))

        return render_template("new_wire.html")

    return app


app = create_app()

if __name__ == "__main__":
    app.run(debug=True)