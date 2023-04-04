from typing import TypeVar

from database_setup_tools.session_manager import SessionManager
from sqlmodel_repository import SQLModelEntity, BaseRepository
from tests.config import POSTGRESQL_DATABASE_URI


ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)
session_manager = SessionManager(database_uri=POSTGRESQL_DATABASE_URI)


class AbstractBaseRepository(BaseRepository[ExampleEntity]):
    """Example base class for all repositories"""

    def __init__(self):
        super().__init__(get_session=session_manager.get_session)
