from typing import TypeVar

from database_setup_tools.session_manager import SessionManager
from sqlalchemy.orm import Session
from sqlmodel_repository import SQLModelEntity, BaseRepository
from tests.config import POSTGRESQL_DATABASE_URI


ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)
session_manager = SessionManager(database_uri=POSTGRESQL_DATABASE_URI)


class AbstractBaseRepository(BaseRepository[ExampleEntity]):
    """Example base class for all repositories"""

    def get_session(self) -> Session:
        """Provides a session to work with"""
        return session_manager.get_session()
