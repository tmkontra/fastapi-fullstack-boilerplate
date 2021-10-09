from functools import partial
import logging
from typing import Callable, Optional
import warnings

from fastapi import Request, Response, Cookie, HTTPException, status, Depends
from fastapi.templating import Jinja2Templates

from .database import get_db_session as _get_db_session
from .model import User, UserSession
from . import settings


logger = logging.getLogger(__name__)
_warned = False

def get_db():
    """The database session can alternatively be injected as a
    dependency.

    NOTE: This is not advisable due to possible deadlock issues under
    concurrent load!

    See: https://github.com/tiangolo/fastapi/issues/3205

    TL;DR - mixing the Session lifetime with fastapi's Depends machinery
    reults in unpredicatable behavior. It is difficult to reason about,
    especially when nested/chained dependencies are used (i.e. your 
    dependency depends on a Depends(get_db).)

    I would suggest starting a session in the body of each route.
    """
    global _warned
    if not _warned:
        logger.warn(
            "get_db dependency is unstable, prefer get_db_session instead!"
        )
        _warned = True
    with _get_db_session() as db:
        yield db


SESSION_KEY = "session_id"


def wsgi_admin(request: Request):
    try:
        session_id = request.cookies[SESSION_KEY]
        session = require_session(session_id)
        user = require_login(session)
        admin = require_admin(user)
        return admin
    except:
        return None


def auth_optional(session_id: Optional[str] = Cookie(None)):
    with _get_db_session() as db:
        if session_id:
            session = db.query(UserSession).filter_by(session_id=session_id).first()
            if session and session.active:
                return session
            else:
                return
        else:
            return


def require_session(session_id: Optional[str] = Cookie(None)):
    with _get_db_session() as db:
        if not session_id:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        session = db.query(UserSession).filter_by(session_id=session_id).first()
        if not session or not session.active:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
        return session


def require_login(auth: UserSession = Depends(require_session)):
    with _get_db_session() as db:
        user = db.query(User).get(auth.user_id)
        if not user:
            raise ValueError("Could not find user for current session")
        return user


def require_admin(user: User = Depends(require_login)):
    if not user.is_admin:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return user


Render = Callable[[str, dict], Response]


class RenderTemplate:
    def __init__(self, template_dir=None, **globals):
        template_dir = template_dir or settings.TEMPLATE_DIR
        self._templates = Jinja2Templates(directory=template_dir)
        self._set_globals(self._templates, globals)

    @staticmethod
    def _set_globals(template_cls, globals: dict):
        for key, value in globals.items():
            template_cls.env.globals[key] = value

    def _render(self, request, name, context):
        context.update({"request": request})
        return self._templates.TemplateResponse(name, context)

    def __call__(self, request: Request) -> Render:
        return partial(self._render, request)


Templates = RenderTemplate(APP_NAME=settings.APP_NAME)
