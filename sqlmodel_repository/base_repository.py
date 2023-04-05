from abc import ABC
from contextlib import contextmanager
from functools import lru_cache
from typing import Callable, Generator, Generic, Type, TypeVar, get_args

from sqlalchemy.orm import Session

from sqlmodel_repository.entity import SQLModelEntity
from sqlmodel_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityNotFoundException

GenericEntity = TypeVar("GenericEntity", bound=SQLModelEntity)


class BaseRepository(Generic[GenericEntity], ABC):
    """Abstract base class for all repositories"""

    entity: Type[GenericEntity]

    def __init__(self, get_session: Callable[..., Generator[Session, None, None]]):
        self.get_session = get_session
        self.entity = self._entity_class()

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager that provides a session to the caller

        Returns:
            Generator[Session, None, None]: A session object
        """
        session = next(self.get_session())
        try:
            yield session
        except:
            session.rollback()
            raise

    def _update(self, entity: GenericEntity, **kwargs) -> GenericEntity:
        """Updates an entity with the given attributes (keyword arguments) if they are not None

        Args:
            entity (Entity): The entity to update
            **kwargs: The attributes to update with their new values

        Returns:
            GenericEntity: The updated entity

        Raises:
            EntityNotFoundException: If the entity was not found in the database

        Notes:
            This method must use the same context to fetch and update the entity. Otherwise its detached and may not be updated.
        """

        with self.session() as session:
            entity = self._get_with_session_context(session=session, entity_id=entity.id)

            for key, value in kwargs.items():
                if value is not None:
                    setattr(entity, key, value)
            session.commit()
            session.refresh(entity)

        return entity

    def _get_with_session_context(self, session: Session, entity_id: int) -> GenericEntity:
        """Retrieves an entity from the database with the specified ID.

        Args:
            session (Session): The session to use to retrieve the entity.
            entity_id (int): The ID of the entity to retrieve.

        Returns:
            GenericEntity: A GenericEntity object with the specified ID.

        Raises:
            EntityNotFoundException: If no entity with the specified ID is found in the database.
        """
        result = session.query(self.entity).filter(self.entity.id == entity_id).one_or_none()
        if result is None:
            raise EntityNotFoundException(f"Entity {GenericEntity.__name__} with ID {entity_id} not found")
        return result

    def _get(self, entity_id: int) -> GenericEntity:
        """Retrieves an entity from the database with the specified ID.

        Args:
            entity_id (int): The ID of the entity to retrieve.

        Returns:
            GenericEntity: Object with the specified ID.

        Raises:
            EntityNotFoundException: If the entity was not found in the database
        """
        with self.session() as session:
            result = self._get_with_session_context(session=session, entity_id=entity_id)
        return result

    # pylint: disable=dangerous-default-value
    def _get_all(self, filters: list = []) -> list[GenericEntity]:
        """Retrieves a list of entities from the database that match the specified filters.

        Args:
            filters (list): An optional list of attribute-value pairs used to filter the query. Default is an empty list.

        Returns:
            list[GenericEntity]: A list of GenericEntity objects that match the specified filters.
        """
        with self.session() as session:
            result = session.query(self.entity).filter(*filters).all()
        return result

    def _create(self, entity: GenericEntity) -> GenericEntity:
        """Adds a new entity to the database.

        Args:
            entity (GenericEntity): A GenericEntity object to add to the database.

        Returns:
             GenericEntity: The object that was added to the database, with any auto-generated fields populated.

        Raises:
            CouldNotCreateEntityException: If there was an error inserting the entity into the database.
        """
        with self.session() as session:
            try:
                session.add(entity)
                session.commit()
                session.refresh(entity)
                return entity
            except Exception as exception:
                raise CouldNotCreateEntityException from exception

    def _delete(self, entity: GenericEntity) -> GenericEntity:
        """Deletes an entity from the database.

        Args:
            entity (GenericEntity): A GenericEntity object to delete from the database.

        Returns:
            GenericEntity: The object that was deleted from the database.

        Raises:
            DatabaseError: If there was an error deleting the entity from the database.
        """
        with self.session() as session:
            try:
                session.delete(entity)
                session.commit()
                return entity
            except Exception as exception:
                raise CouldNotDeleteEntityException from exception

    @classmethod
    @lru_cache(maxsize=1)
    def _entity_class(cls) -> Type[GenericEntity]:
        """Retrieves the actual entity class at runtime. This function may or may not be victim of future Python changes.

        Returns:
            Type[GenericEntity]: The managed entity class for the repository
        """
        generic_alias = getattr(cls, "__orig_bases__")[0]
        entity_class = get_args(generic_alias)[0]

        if not issubclass(entity_class, SQLModelEntity):
            raise TypeError(f"Entity class {entity_class} for {cls.__name__} must be a subclass of {SQLModelEntity}")

        return entity_class  # type: ignore
