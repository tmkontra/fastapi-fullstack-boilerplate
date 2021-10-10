from fastapi import FastAPI, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_static_digest import StaticDigest
import sqlalchemy

from . import settings
from .admin import admin_app
from .database import Session, get_db_session
from .dependencies import get_db, Templates, Render
from .ext import cbv
from .model import User


web = APIRouter()


@cbv(web)
class WebRoutes:
    render: Render = Depends(Templates)

    @web.get("/")
    def home(deps):
        # example of manual db session
        with get_db_session() as db:
            user_count = db.query(User).count()
        context = {
            "message": "Hello",
            "user_count": user_count,
        }
        return deps.render("home.html", context)


api = APIRouter()


@cbv(api)
class APIRoutes:
    # example of injected db session
    db: Session = Depends(get_db)

    @api.get("/")
    def index(deps):
        rand_result = list(deps.db.execute(sqlalchemy.text("""select RANDOM();""")))
        rand = rand_result[0][0]
        return {"success": True, "value": rand}


def create_app():
    app = FastAPI(
        title=settings.APP_NAME, 
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    static_digest = StaticDigest(source_dir=settings.STATIC_DIR)
    static_files = StaticFiles(directory=static_digest.directory)
    app.include_router(web, include_in_schema=False)
    app.include_router(api, prefix="/api")
    app.mount(path="/admin", app=admin_app)
    app.mount("/static", static_files, name="static")

    return app
