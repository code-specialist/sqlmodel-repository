from typing import TypeVar

from sqlalchemy.orm import Session
from sqlmodel_repository import Repository, SQLModelEntity


ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)


class AbstractRepository(Repository[ExampleEntity]):
    """Example base class for all repositories"""
