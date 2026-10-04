"""Login, CSRF protection and security headers (no extra dependencies)."""
import hmac
import secrets
from urllib.parse import urlparse

from flask import (
    Blueprint, abort, current_app, flash, redirect, render_template, request,
    session, url_for,
)
from markupsafe import Markup

PUBLIC_ENDPOINTS = {"auth.login", "auth.health", "static"}


def csrf_token():
    if "csrf" not in session:
        session["csrf"] = secrets.token_hex(16)
    return session["csrf"]


def csrf_input():
    return Markup(f'<input type="hidden" name="csrf_token" value="{csrf_token()}">')


def _safe_next(target):
    if not target or not target.startswith("/") or target.startswith("//"):
        return None
    parsed = urlparse(target)
    return target if not parsed.netloc and not parsed.scheme else None


def init_security(app):
    auth = Blueprint("auth", __name__)

    @auth.route("/login", methods=["GET", "POST"])
    def login():
        if request.method == "POST":
            expected = current_app.config["APP_PASSWORD"] or ""
            given = request.form.get("password", "")
            if expected and hmac.compare_digest(given.encode(), expected.encode()):
                session.clear()
                session["auth"] = True
                session.permanent = True
                return redirect(
                    _safe_next(request.args.get("next")) or url_for("dashboard.dashboard")
                )
            flash("Incorrect password.", "danger")
            return render_template("login.html"), 401
        return render_template("login.html")

    @auth.route("/logout", methods=["POST"])
    def logout():
        session.clear()
        return redirect(url_for("auth.login"))

    @auth.route("/healthz")
    def health():
        return "ok"

    app.register_blueprint(auth)
    app.jinja_env.globals["csrf_input"] = csrf_input
    app.jinja_env.globals["auth_enabled"] = lambda: bool(app.config["APP_PASSWORD"])

    @app.before_request
    def guard():
        if request.method == "POST":
            sent = request.form.get("csrf_token", "")
            expected = session.get("csrf", "")
            if not expected or not hmac.compare_digest(sent, expected):
                abort(400, "Invalid or missing security token. Reload the page and try again.")

        if app.config["APP_PASSWORD"] and request.endpoint not in PUBLIC_ENDPOINTS:
            if not session.get("auth"):
                return redirect(url_for("auth.login", next=request.full_path.rstrip("?")))

    @app.after_request
    def headers(resp):
        resp.headers.setdefault("X-Content-Type-Options", "nosniff")
        resp.headers.setdefault("X-Frame-Options", "DENY")
        resp.headers.setdefault("Referrer-Policy", "same-origin")
        if app.config["IS_PRODUCTION"]:
            resp.headers.setdefault("Strict-Transport-Security", "max-age=31536000")
        if request.endpoint != "static":
            resp.headers.setdefault("Cache-Control", "no-store")
        return resp

    @app.errorhandler(400)
    @app.errorhandler(404)
    @app.errorhandler(500)
    def error_page(err):
        code = getattr(err, "code", 500)
        message = getattr(err, "description", None) if code != 500 else "Something went wrong on our side."
        return render_template("error.html", code=code, message=message), code
