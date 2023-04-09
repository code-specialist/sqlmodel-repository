from abc import ABC, abstractmethod

from functools import lru_cache
from typing import Generic, Type, TypeVar, get_args

from sqlalchemy.orm import Session

from sqlmodel_repository.entity import SQLModelEntity
from sqlmodel_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityDoesNotPossessAttributeException, EntityNotFoundException

GenericEntity = TypeVar("GenericEntity", bound=SQLModelEntity)


class BaseRepository(Generic[GenericEntity], ABC):
    """Abstract base class for all repositories"""

    entity: Type[GenericEntity]

    def __init__(self):
        self.entity = self._entity_class()

    @abstractmethod
    def get_session(self) -> Session:
        """Provides a session to work with"""
        raise NotImplementedError

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
        session = self.get_session()
        entity = self._get(entity_id=entity.id)

        for key, value in kwargs.items():
            if value is not None:
                try:
                    setattr(entity, key, value)
                except Exception as exception:
                    raise EntityDoesNotPossessAttributeException(f"Could not set attribute {key} to {value} on entity {entity}") from exception

        session.commit()
        session.refresh(entity)

        return entity

    def _update_batch(self, entities: list[GenericEntity], **kwargs) -> list[GenericEntity]:
        """Updates a list of entities with the given attributes (keyword arguments) if they are not None

        Args:
            entities (list[GenericEntity]): The entities to update
            **kwargs: The attributes to update with their new values

        Returns:
            list[GenericEntity]: The updated entities
        """

        session = self.get_session()

        for entity in entities:
            for key, value in kwargs.items():
                if value is not None:
                    try:
                        setattr(entity, key, value)
                    except Exception as exception:
                        raise EntityDoesNotPossessAttributeException(f"Could not set attribute {key} to {value} on entity {entity}") from exception

        session.commit()

        for entity in entities:
            session.refresh(entity)

        return entities

    def _get(self, entity_id: int) -> GenericEntity:
        """Retrieves an entity from the database with the specified ID.

        Args:
            entity_id (int): The ID of the entity to retrieve.

        Returns:
            GenericEntity: Object with the specified ID.

        Raises:
            EntityNotFoundException: If the entity was not found in the database
        """
        session = self.get_session()
        result = session.query(self.entity).filter(self.entity.id == entity_id).one_or_none()
        if result is None:
            raise EntityNotFoundException(f"Entity {GenericEntity.__name__} with ID {entity_id} not found")
        return result

    # pylint: disable=dangerous-default-value
    def _get_batch(self, filters: list = []) -> list[GenericEntity]:
        """Retrieves a list of entities from the database that match the specified filters.

        Args:
            filters (list): An optional list of attribute-value pairs used to filter the query. Default is an empty list.

        Returns:
            list[GenericEntity]: A list of GenericEntity objects that match the specified filters.
        """
        session = self.get_session()
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
        session = self.get_session()

        try:
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception as exception:
            session.rollback()
            raise CouldNotCreateEntityException from exception

    def _create_batch(self, entities: list[GenericEntity]) -> list[GenericEntity]:
        """Adds a batch of new entities to the database.

        Args:
            entities (list[GenericEntity]): A list of GenericEntity objects to add to the database.

        Returns:
            list[GenericEntity]: The objects that were added to the database, with any auto-generated fields populated.
        """
        session = self.get_session()
        try:
            for entity in entities:
                session.add(entity)

            session.commit()
        except Exception as exception:
            session.rollback()
            raise CouldNotCreateEntityException from exception

        for entity in entities:
            session.refresh(entity)
        return entities

    def _delete(self, entity: GenericEntity) -> GenericEntity:
        """Deletes an entity from the database.

        Args:
            entity (GenericEntity): A GenericEntity object to delete from the database.

        Returns:
            GenericEntity: The object that was deleted from the database.

        Raises:
            DatabaseError: If there was an error deleting the entity from the database.
        """
        session = self.get_session()
        try:
            session.delete(entity)
            session.commit()
            return entity
        except Exception as exception:
            session.rollback()
            raise CouldNotDeleteEntityException from exception

    def _delete_batch(self, entities: list[GenericEntity]) -> None:
        """Deletes a batch of entities from the database.

        Args:
            entities (list[GenericEntity]): A list of GenericEntity objects to delete from the database.

        Raises:
            CouldNotDeleteEntityException: If there was an error deleting the entities from the database.
        """
        session = self.get_session()

        try:
            for entity in entities:
                session.delete(entity)

            session.commit()
        except Exception as exception:
            session.rollback()
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
