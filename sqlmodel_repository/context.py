from contextvars import ContextVar
from database_setup_tools.session_manager import SessionManager
from sqlalchemy.orm import Session

from sqlmodel_repository.config import POSTGRESQL_DATABASE_URI

session_context: ContextVar[dict] = ContextVar("request_context", default={})
session_manager = SessionManager(database_uri=POSTGRESQL_DATABASE_URI)


def _get_session() -> Session:
    """Retrieve the session from the thread context"""
    context = session_context.get()
    return context.get("session")  # type: ignore


def _set_session(session: Session):
    context = session_context.get()
    context["session"] = session


def get_session() -> Session:
    """Provides a session to work with"""
    session = _get_session()
    if session is None:
        session = next(session_manager.get_session())
        _set_session(session)
    return session
