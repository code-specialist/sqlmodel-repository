from abc import ABC
from typing import List, TypeVar

from sqlmodel import col

from sqlmodel_repository.base_repository import BaseRepository
from sqlmodel_repository.entity import SQLModelEntity

GenericEntity = TypeVar("GenericEntity", bound=SQLModelEntity)


class Repository(BaseRepository[GenericEntity], ABC):
    """Abstract base class for repository implementations"""

    def get_batch_by_ids(self, entity_ids: list[int]) -> List[GenericEntity]:
        """Get multiple entities with one query by IDs

        Args:
            entity_ids (List[int]): IDs of the entities

        Returns:
            List[GenericEntity]: The entities that were found in the repository for the given IDs
        """
        filters = [col(self._entity_class().id).in_(entity_ids)]
        return self.get_batch(filters=filters)

    def get_all(self) -> List[GenericEntity]:
        """Get all entities of the repository

        Returns:
            List[GenericEntity]: All entities that were found in the repository
        """
        return self.get_batch()

    def update_batch_by_ids(self, entity_ids: list[int], **kwargs) -> list[GenericEntity]:
        """Update multiple entities with the same target values

        Args:
            entities (list[GenericEntity]): Entities to update
            **kwargs: Any new values

        Returns:
            list[GenericEntity]: The updated entities
        """
        entities = self.get_batch_by_ids(entity_ids=entity_ids)
        return self.update_batch(entities=entities, **kwargs)

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

    def delete_by_id(self, entity_id: int) -> None:
        """Delete an entity by entity_id

        Args:
            entity_id (int): ID of the entity

        Raises:
            NoResultFound: If no entity was found
        """
        entity_to_delete = self.get(entity_id=entity_id)
        self.delete(entity=entity_to_delete)

    def delete_batch_by_ids(self, entity_ids: List[int]):
        """Delete an entity by entity_id

        Args:
            entity_ids (List[int]): IDs of the entities
        """
        entities_to_delete = self.get_batch_by_ids(entity_ids=entity_ids)
        self.delete_batch(entities=entities_to_delete)
