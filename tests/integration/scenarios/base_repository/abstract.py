from typing import TypeVar

from sqlalchemy.orm import Session

from sqlmodel_repository.context import get_session as contextual_session
from sqlmodel_repository import SQLModelEntity, BaseRepository

ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)


class AbstractBaseRepository(BaseRepository[ExampleEntity]):
    """Example base class for all repositories"""

    def get_session(self) -> Session:
        """Provides a session to work with"""
        return contextual_session()
