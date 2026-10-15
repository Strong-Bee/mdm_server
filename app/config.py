import os


_BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
_DATABASE_PATH = os.path.join(_BASE_DIR, "mdm.db")


class Config:
    DATABASE = os.environ.get("MDM_DATABASE_PATH", _DATABASE_PATH)
    SQLALCHEMY_DATABASE_URI = "sqlite:///" + DATABASE.replace("\\", "/")
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SECRET_KEY = os.environ.get("FLASK_SECRET_KEY")
    MDM_ADMIN_TOKEN = os.environ.get("MDM_ADMIN_TOKEN")
