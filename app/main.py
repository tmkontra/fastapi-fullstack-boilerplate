from fastapi import FastAPI, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
import sqlalchemy

from . import settings
from .admin import admin_app
from .database import Session
from .dependencies import get_db_session, Templates, Render
from .ext import cbv


web = APIRouter()


@cbv(web)
class WebRoutes:
    render: Render = Depends(Templates)

    @web.get("/")
    def home(deps):
        context = {
            "message": "Hello",
        }
        return deps.render("home.html", context)


api = APIRouter()


@cbv(api)
class APIRoutes:
    db: Session = Depends(get_db_session)

    @api.get("/")
    def index(deps):
        rand_result = list(deps.db.execute(sqlalchemy.text("""select RANDOM();""")))
        rand = rand_result[0][0]
        return {"success": True, "value": rand}


def create_app():
    app = FastAPI(
        title=settings.APP_NAME, openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    app.include_router(web, include_in_schema=False)
    app.include_router(api, prefix="/api")
    app.mount(path="/admin", app=admin_app)
    app.mount("/static", StaticFiles(directory=settings.STATIC_DIR), name="static")

    return app
