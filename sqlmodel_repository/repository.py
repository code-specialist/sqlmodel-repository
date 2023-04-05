from abc import ABC
from typing import Callable, Generator, List, TypeVar

from sqlalchemy.orm import Session
from sqlmodel import col
from sqlmodel_repository.base_repository import BaseRepository

from sqlmodel_repository.entity import SQLModelEntity

GenericEntity = TypeVar("GenericEntity", bound=SQLModelEntity)


class Repository(BaseRepository[GenericEntity], ABC):
    """Abstract base class for repository implementations"""

    def __init__(self, get_session: Callable[..., Generator[Session, None, None]]):
        super().__init__(get_session=get_session)

    def create(self, entity: GenericEntity) -> GenericEntity:
        """Creates an entity to the repository

        Args:
            entity (GenericEntity): The entity to add

        Returns:
            GenericEntity: The added entity

        Raises:
            CouldNotCreateEntityException: If the entity could not be created
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
        filters = [col(self._entity_class().id).in_(entity_ids)]
        return self._get_all(filters=filters)

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