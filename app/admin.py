from typing import Sequence
from fastapi import FastAPI, Request, HTTPException, status, Response
from fastapi.middleware.wsgi import WSGIMiddleware
import flask
import flask_admin
from wtforms.fields import StringField
from wtforms import validators
from flask_admin.contrib.sqla import ModelView


from .database import SessionLocal
from .dependencies import wsgi_admin
from .model import User, UserSession
from .settings import APP_NAME, DEBUG_ADMIN, SECRET_KEY
from .services import user_service


class UserAdmin(ModelView):
    form_excluded_columns = [
        "password_hash",
    ]
    form_extra_fields = {"Password": StringField("Password", [validators.DataRequired()])}

    def on_model_change(self, form, model: User, is_created):
        hashed = user_service.hash_password(form["Password"].data)
        model.password_hash = hashed


ADMIN_MODELS = [(User, UserAdmin), UserSession]


def create_admin_app():
    app = flask.Flask(__name__)
    app.secret_key = SECRET_KEY
    admin = flask_admin.Admin(
        name=f"{APP_NAME} Admin", template_mode="bootstrap3", url="/"
    )
    session = SessionLocal()

    def view(model):
        if isinstance(model, Sequence):
            model, view_class = model
            return admin.add_view(view_class(model, session))
        else:
            return admin.add_view(ModelView(model, session))

    for model in ADMIN_MODELS:
        view(model)
    admin.init_app(app)
    return app


admin_app_wsgi = WSGIMiddleware(create_admin_app())

admin_app = FastAPI()


@admin_app.middleware("http")
async def admin_auth_middleware(request: Request, call_next):
    try:
        if wsgi_admin(request) or DEBUG_ADMIN:
            response = await call_next(request)
            return response
        else:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    except:
        return Response(status_code=401)


admin_app.mount(path="/", app=admin_app_wsgi, name="admin_app")
