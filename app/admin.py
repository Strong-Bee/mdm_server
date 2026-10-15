import hmac
import os

from flask import abort, jsonify, request, session
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class ProtectedModelView(ModelView):
    def is_accessible(self):
        return session.get("mdm_admin_authenticated") is True

    def inaccessible_callback(self, name, **kwargs):
        abort(403)


def setup_admin(app):
    db.init_app(app)
    admin = Admin(app, name="MDM Admin", template_mode="bootstrap3")

    class Device(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        serial = db.Column(db.String(64))
        udid = db.Column(db.String(128), unique=True)
        ip = db.Column(db.String(64))
        timestamp = db.Column(db.String(64))
        al_bypass_code = db.Column(db.Text)
        push_token = db.Column(db.Text)

    class Command(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        udid = db.Column(db.String(128))
        command_uuid = db.Column(db.String(128), unique=True)
        command_type = db.Column(db.String(64))
        payload = db.Column(db.Text)
        status = db.Column(db.String(32))

    admin.add_view(ProtectedModelView(Device, db.session))
    admin.add_view(ProtectedModelView(Command, db.session))

    @app.post("/api/admin/login")
    def admin_login():
        expected = app.config.get("MDM_ADMIN_TOKEN") or os.environ.get("MDM_ADMIN_TOKEN")
        data = request.get_json(silent=True)
        supplied = data.get("token", "") if isinstance(data, dict) else ""
        if not expected:
            return jsonify(error="Admin login is disabled: MDM_ADMIN_TOKEN is not configured"), 503
        if not isinstance(supplied, str) or not supplied or not hmac.compare_digest(supplied, expected):
            return jsonify(error="Unauthorized"), 401
        session.clear()
        session["mdm_admin_authenticated"] = True
        return jsonify(status="authenticated"), 200

    @app.post("/api/admin/logout")
    def admin_logout():
        session.clear()
        return jsonify(status="logged_out"), 200

    with app.app_context():
        db.create_all()
