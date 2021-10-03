import os
import pathlib

APP_NAME = "My App"
API_V1_STR = "/api/v1"
SQLALCHEMY_URL = os.environ["DB_URL"]
SQLALCHEMY_USER = os.environ["DB_USER"]
SQLALCHEMY_PASSWORD = os.environ["DB_PASSWORD"]
APP_ROOT = pathlib.Path(__file__).parent
TEMPLATE_DIR = APP_ROOT / "templates"
STATIC_DIR = APP_ROOT / "static"
SECRET_KEY = os.environ["SECRET_KEY"]
DEBUG_ADMIN = os.environ.get("DEBUG_ADMIN", False)
