from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def setup_admin(app):
    db.init_app(app)
    admin = Admin(app, name='MDM Admin', template_mode='bootstrap3')

    class Device(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        serial = db.Column(db.String(64))
        udid = db.Column(db.String(128))
        ip = db.Column(db.String(64))
        timestamp = db.Column(db.String(64))
        al_bypass_code = db.Column(db.Text)
        push_token = db.Column(db.Text)

    class Command(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        udid = db.Column(db.String(128))
        command_uuid = db.Column(db.String(128))
        command_type = db.Column(db.String(64))
        payload = db.Column(db.Text)
        status = db.Column(db.String(32))

    admin.add_view(ModelView(Device, db.session))
    admin.add_view(ModelView(Command, db.session))

    with app.app_context():
        db.create_all()
