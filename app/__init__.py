from flask import Flask
from .db import init_db
from .routes import mdm_bp
from .admin import setup_admin

def create_app():
    app = Flask(__name__)
    app.config.from_object('app.config.Config')
    init_db(app)
    setup_admin(app)
    app.register_blueprint(mdm_bp)
    return app
