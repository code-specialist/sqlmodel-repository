from abc import ABC
from functools import lru_cache
from typing import TypeVar, Generic, Type, get_args, List

from sqlalchemy.orm import Session
from sqlmodel import col

from python_repository.entity import SQLModelEntity

GenericEntity = TypeVar("GenericEntity", SQLModelEntity, SQLModelEntity)  # must be multiple constraints


class Repository(Generic[GenericEntity], ABC):
    """ Abstract base class for repository implementations """

    @classmethod
    def create(cls, entity: GenericEntity, session: Session) -> GenericEntity:
        """ Creates an entity to the repository

        Args:
            session (Session): Database session to use
            entity (GenericEntity): The entity to add

        Returns:
            GenericEntity: The added entity
        """
        entity = cls._entity_class()(**entity.__dict__)
        session.add(entity)
        session.commit()
        session.refresh(entity)
        return entity

    @classmethod
    def get(cls, entity_id: int, session: Session) -> GenericEntity:
        """ Get an entity by ID

        Args:
            entity_id (int): The ID of the entity
            session (Session): Database session to use

        Returns:
            GenericEntity: The entity

        Raises:
            NoResultFound: If no entity was found
        """
        return session \
            .query(cls._entity_class()) \
            .filter(cls._entity_class().id == entity_id) \
            .one()

    @classmethod
    def get_batch(cls, entity_ids: List[int], session: Session) -> List[GenericEntity]:
        """ Get multiple entities with one query by IDs

        Args:
            entity_ids (List[int]): IDs of the entities
            session (Session): Database session to use

        Returns:
            List[GenericEntity]: The entities that were found in the repository for the given IDs
        """
        return session \
            .query(cls._entity_class()) \
            .filter(col(cls._entity_class().id).in_(entity_ids)) \
            .all()

    @classmethod
    def get_all(cls, session: Session) -> List[GenericEntity]:
        """ Get all entities of the repository

        Args:
            session (Session): Database session to use

        Returns:
            List[GenericEntity]: All entities that were found in the repository
        """
        return session \
            .query(cls._entity_class()) \
            .all()

    # noinspection PyShadowingBuiltins
    @classmethod
    def update(cls, entity: GenericEntity, updates: GenericEntity, session: Session, allowed_attributes: List[str] = None) -> GenericEntity:
        """ Update an entity

        Args:
            entity (GenericEntity): Entity to update
            updates (GenericEntity): Instance containing new values for the entity
            session (Session): Database session to use
            allowed_attributes (Optional[List[str]]): List of attributes that are allowed to be updated. If not provided, all attributes are allowed.

        Returns:
            GenericEntity: The updated entity
        """
        not_allowed_attributes = {"entity_id", "_sa_instance_state"}

        if allowed_attributes is None:
            allowed_attributes = entity.__dict__.keys()

        for key, value in updates.__dict__.items():
            if key in allowed_attributes and key not in not_allowed_attributes:
                setattr(entity, key, value)

        session.commit()
        session.refresh(entity)
        return entity

    # noinspection PyShadowingBuiltins
    @classmethod
    def update_by_id(cls, entity_id: int, updates: GenericEntity, session: Session, allowed_attributes: List[str] = None) -> GenericEntity:
        """ Update an entity

        Args:
            entity_id (int): The entity_id of the entity to update
            updates (GenericEntity): Instance containing new values for the entity
            session (Session): Database session to use
            allowed_attributes (Optional[List[str]]): A List of attributes that are allowed to be updated. If none are provided all attributes are allowed. Defaults to None.

        Returns:
            GenericEntity: The updated entity
        """
        entity_to_update = cls.get(entity_id=entity_id, session=session)
        return cls.update(entity=entity_to_update, updates=updates, session=session, allowed_attributes=allowed_attributes)

    @classmethod
    def delete(cls, entity: GenericEntity, session: Session) -> None:
        """ Delete an entity

        Args:
            entity (GenericEntity): Entity to delete
            session (Session): Database session to use
        """
        session.delete(entity)
        session.commit()

    # noinspection PyShadowingBuiltins
    @classmethod
    def delete_by_id(cls, entity_id: int, session: Session) -> None:
        """ Delete an entity by entity_id

        Args:
            entity_id (int): ID of the entity
            session (Session): Database session to use

        Raises:
            NoResultFound: If no entity was found
        """
        entity_to_delete = cls.get(entity_id=entity_id, session=session)
        cls.delete(entity=entity_to_delete, session=session)

    @classmethod
    def delete_batch(cls, entities: List[GenericEntity], session: Session):
        """ Delete multiple entities with one commit

        Args:
            entities (List[GenericEntity]): Entities to delete
            session (Session): Database session to use
        """
        for to_delete in entities:
            session.delete(to_delete)
        session.commit()

    @classmethod
    def delete_batch_by_ids(cls, entity_ids: List[int], session: Session):
        """ Delete an entity by entity_id

        Args:
            entity_ids (List[int]): IDs of the entities
            session (Session): Database session to use
        """
        entities_to_delete = cls.get_batch(entity_ids=entity_ids, session=session)
        cls.delete_batch(entities=entities_to_delete, session=session)

    @classmethod
    @lru_cache(maxsize=1)
    def _entity_class(cls) -> Type[GenericEntity]:
        """ Retrieves the actual entity class at runtime """
        generic_alias = getattr(cls, "__orig_bases__")[0]
        entity_class = get_args(generic_alias)[0]

        if not issubclass(entity_class, SQLModelEntity):
            raise TypeError(f"Entity class {entity_class} for {cls.__name__} must be a subclass of {SQLModelEntity}")

        return entity_class
