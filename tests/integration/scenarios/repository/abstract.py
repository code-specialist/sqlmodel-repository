from typing import TypeVar

from sqlalchemy.orm import Session

from sqlmodel_repository import SQLModelEntity, Repository

ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)


class AbstractRepository(Repository[ExampleEntity]):
    """Example base class for all repositories"""

    def __init__(self, session: Session):
        super().__init__()
        self.session = session

    def get_session(self) -> Session:
        """Provides a session to work with"""
        return self.session
