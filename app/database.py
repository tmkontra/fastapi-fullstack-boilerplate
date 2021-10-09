from contextlib import contextmanager
from typing import Callable
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm.session import Session

from .settings import SQLALCHEMY_URL, SQLALCHEMY_USER, SQLALCHEMY_PASSWORD

SQLALCHEMY_DATABASE_URL = SQLALCHEMY_URL

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args=dict(user=SQLALCHEMY_USER, password=SQLALCHEMY_PASSWORD),
)

SessionLocal: Callable[..., Session] = sessionmaker(
    autocommit=False, autoflush=False, bind=engine
)

Base = declarative_base()

@contextmanager
def get_db_session():
    """Starts a database session as a context manager.
    """
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()