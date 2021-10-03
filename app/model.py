from datetime import datetime
from sqlalchemy import DateTime, Column, String, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text


from .database import Base
from .ext import Model, PkModel, reference_col


_utcnow = text("(now() at time zone 'utc')")


class Timestamps(Model):
    __abstract__ = True

    created_at = Column(DateTime, nullable=False, server_default=_utcnow)
    updated_at = Column(
        DateTime, nullable=False, server_default=_utcnow, onupdate=_utcnow
    )

    @property
    def created_on(self):
        return self.created_at.date()


class User(PkModel, Timestamps, Base):
    __tablename__ = "user"

    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    deleted_at = Column(DateTime, nullable=True)
    is_admin = Column(Boolean, default=False, nullable=False)


class UserSession(PkModel, Timestamps, Base):
    __tablename__ = "user_session"

    user_id = reference_col("user")
    session_id = Column(String, index=True)
    expires_at = Column(DateTime, nullable=False)
    logged_out_at = Column(DateTime, nullable=True)

    User = relationship("User", backref="sessions")

    @property
    def active(self):
        now = datetime.utcnow()
        return (self.expires_at > now) and (self.logged_out_at is None)

    def log_out(self, db):
        db.query(UserSession).filter_by(id=self.id).update(
            {"logged_out_at": datetime.utcnow()}
        )
