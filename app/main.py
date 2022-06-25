import sqlalchemy
from fastapi import FastAPI, Depends, APIRouter
from fastapi.staticfiles import StaticFiles
from fastapi_jinja_utils import Jinja2TemplatesDependency, Renderable
from fastapi_static_digest import StaticDigest
from fastapi_utils.cbv import cbv

from . import settings
from .admin import admin_app
from .database import Session, get_db_session
from .dependencies import get_db
from .model import User

web = APIRouter()

Templates = Jinja2TemplatesDependency(template_dir=settings.TEMPLATE_DIR)


@cbv(web)
class WebRoutes:
    render: Renderable = Depends(Templates)

    @web.get("/")
    def home(deps):
        # example of manual db session
        try:
            with get_db_session() as db:
                user_count = db.query(User).count()
        except:
            user_count = "<no db connection>"
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
