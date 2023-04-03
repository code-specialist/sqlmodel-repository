from abc import ABC
from contextlib import contextmanager
from functools import lru_cache
from typing import Callable, Generator, TypeVar, Generic, Type, get_args, List

from sqlalchemy.orm import Session
from sqlmodel import col

from python_repository.entity import SQLModelEntity
from python_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityNotFoundException

GenericEntity = TypeVar("GenericEntity", SQLModelEntity, SQLModelEntity)  # must be multiple constraints


class BaseRepository(Generic[GenericEntity], ABC):
    """Abstract base class for all repositories"""

    entity: GenericEntity

    def __init__(self, get_session: Callable[..., Generator[Session, None, None]]) -> None:
        self.get_session = get_session

    @contextmanager
    def session(self) -> Generator[Session, None, None]:
        """Context manager that provides a session to the caller"""
        session = next(self.get_session())
        try:
            yield session
        except:
            session.rollback()
            raise
        finally:
            session.close()

    def _update(self, entity: GenericEntity, **kwargs) -> GenericEntity:
        """Updates an entity with the given attributes (keyword arguments) if they are not None

        Args:
            entity (Entity): The entity to update
            **kwargs: The attributes to update with their new values

        Returns:
            Entity: The updated entity
        """
        with self.session() as session:

            for key, value in kwargs.items():
                if value is not None:
                    setattr(entity, key, value)
            session.commit()
            session.refresh(entity)

        return entity

    def _get(self, entity_id: int) -> GenericEntity:
        """Retrieves an entity from the database with the specified ID.

        Args:
            entity_id: The ID of the entity to retrieve.

        Returns:
            A GenericEntity object with the specified ID.

        Raises:
            EntityNotFoundException: If no entity with the specified ID is found in the database.
        """
        with self.session() as session:
            result = session.query(self.entity).filter(self.entity.id == entity_id).one_or_none()

        if result is None:
            raise EntityNotFoundException(f"Entity {GenericEntity.__name__} with ID {entity_id} not found")

        return result

    def _get_all(self, filters: list = []) -> list[GenericEntity]:
        """Retrieves a list of entities from the database that match the specified filters.

        Args:
            filters: An optional list of attribute-value pairs used to filter the query. Default is an empty list.

        Returns:
            A list of GenericEntity objects that match the specified filters.
        """
        with self.session() as session:
            return session.query(self.entity).filter_by(*filters).all()

    def _create(self, entity: GenericEntity) -> GenericEntity:
        """Adds a new entity to the database.

        Args:
            entity: A GenericEntity object to add to the database.

        Returns:
            The GenericEntity object that was added to the database, with any auto-generated fields populated.

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
            entity: A GenericEntity object to delete from the database.

        Returns:
            The GenericEntity object that was deleted from the database.

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
        """Retrieves the actual entity class at runtime. This function may or may not be victim of future Python changes."""
        generic_alias = getattr(cls, "__orig_bases__")[0]
        entity_class = get_args(generic_alias)[0]

        if not issubclass(entity_class, SQLModelEntity):
            raise TypeError(f"Entity class {entity_class} for {cls.__name__} must be a subclass of {SQLModelEntity}")

        return entity_class


class Repository(Generic[GenericEntity], BaseRepository[GenericEntity], ABC):
    """Abstract base class for repository implementations"""

    def create(self, entity: GenericEntity) -> GenericEntity:
        """Creates an entity to the repository

        Args:
            entity (GenericEntity): The entity to add

        Returns:
            GenericEntity: The added entity
        """
        return self._create(entity=entity)

    def get(self, entity_id: int) -> GenericEntity:
        """Get an entity by ID

        Args:
            entity_id (int): The ID of the entity

        Returns:
            GenericEntity: The entity

        Raises:
            NoResultFound: If no entity was found
        """
        return self._get(entity_id=entity_id)

    def get_batch(self, entity_ids: list[int]) -> List[GenericEntity]:
        """Get multiple entities with one query by IDs

        Args:
            entity_ids (List[int]): IDs of the entities

        Returns:
            List[GenericEntity]: The entities that were found in the repository for the given IDs
        """
        filter_ = [col(self._entity_class().id).in_(entity_ids)]
        return self._get_all(filters=filter_)

    def get_all(self) -> List[GenericEntity]:
        """Get all entities of the repository

        Returns:
            List[GenericEntity]: All entities that were found in the repository
        """
        return self._get_all()

    # noinspection PyShadowingBuiltins
    def update(self, entity: GenericEntity, **kwargs) -> GenericEntity:
        """Update an entity

        Args:
            entity (GenericEntity): Entity to update
            **kwargs: Any new values

        Returns:
            GenericEntity: The updated entity
        """
        return self._update(entity=entity, **kwargs)

    # noinspection PyShadowingBuiltins
    def update_by_id(self, entity_id: int, **kwargs) -> GenericEntity:
        """Update an entity

        Args:
            entity_id (int): The entity_id of the entity to update
            **kwargs: Any new values

        Returns:
            GenericEntity: The updated entity
        """
        entity_to_update = self.get(entity_id=entity_id)
        return self.update(entity=entity_to_update, **kwargs)

    def delete(self, entity: GenericEntity) -> None:
        """Delete an entity

        Args:
            entity (GenericEntity): Entity to delete
        """
        self._delete(entity=entity)

    def delete_by_id(self, entity_id: int) -> None:
        """Delete an entity by entity_id

        Args:
            entity_id (int): ID of the entity

        Raises:
            NoResultFound: If no entity was found
        """
        entity_to_delete = self.get(entity_id=entity_id)
        self.delete(entity=entity_to_delete)

    def delete_batch(self, entities: List[GenericEntity]):
        """Delete multiple entities with one commit

        Args:
            entities (List[GenericEntity]): Entities to delete
        """
        for to_delete in entities:
            self._delete(to_delete)

    def delete_batch_by_ids(self, entity_ids: List[int]):
        """Delete an entity by entity_id

        Args:
            entity_ids (List[int]): IDs of the entities
        """
        entities_to_delete = self.get_batch(entity_ids=entity_ids)
        self.delete_batch(entities=entities_to_delete)
