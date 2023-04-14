from abc import ABC, abstractmethod
from functools import lru_cache
from typing import Generic, List, Optional, Type, TypeVar, get_args

from sqlalchemy.orm import Session
from sqlmodel import col
from structlog import WriteLogger

from sqlmodel_repository.entity import SQLModelEntity
from sqlmodel_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityDoesNotPossessAttributeException, EntityNotFoundException
from sqlmodel_repository.logger import sqlmodel_repository_logger

GenericEntity = TypeVar("GenericEntity", bound=SQLModelEntity)


class BaseRepository(Generic[GenericEntity], ABC):
    """Abstract base class for all repositories"""
    
    _default_excluded_keys = ["_sa_instance_state"]

    def __init__(self, logger: Optional[WriteLogger] = None, sensitive_attribute_keys: Optional[list[str]] = None):
        """Initializes the repository

        Args:
            logger (Logger, optional): The logger to use. Defaults to None and will use the default logger.
            sensitive_attribute_keys (list[str], optional): A list of attributes that should be excluded from the logs. Defaults to None.

        Notes:
            - The default logger is a structlog logger that logs in JSON format.
            - The default exclusion list (_default_excluded_keys) is ["_sa_instance_state"] which is a default SQLAlchemy attribute that is added to all entities. You may override this.
        """
        self.entity = self._entity_class()
        self.logger = logger if logger is not None else sqlmodel_repository_logger
        self.sensitive_attribute_keys = sensitive_attribute_keys if sensitive_attribute_keys is not None else []

    @abstractmethod
    def get_session(self) -> Session:
        """Provides a session to work with"""
        raise NotImplementedError

    def find(self, **kwargs) -> List[GenericEntity]:
        """Get multiple entities with one query by filters

        Args:
            **kwargs: The filters to apply

        Returns:
            List[GenericEntity]: The entities that were found in the repository for the given filters
        """
        filters = []

        for key, value in kwargs.items():
            try:
                filters.append(col(getattr(self.entity, key)) == value)
            except AttributeError as attribute_error:
                raise EntityDoesNotPossessAttributeException(f"Entity {self.entity} does not have the attribute {key}") from attribute_error
        return self.get_batch(filters=filters)

    def update(self, entity: GenericEntity, **kwargs) -> GenericEntity:
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
        self._emit_log("Updating", entities=[entity], **kwargs)

        entity = self.get(entity_id=entity.id)

        for key, value in kwargs.items():
            if value is not None:
                try:
                    setattr(entity, key, value)
                except Exception as exception:
                    raise EntityDoesNotPossessAttributeException(f"Could not set attribute {key} to {value} on entity {entity}") from exception

        session.commit()
        session.refresh(entity)

        return entity

    def update_batch(self, entities: list[GenericEntity], **kwargs) -> list[GenericEntity]:
        """Updates a list of entities with the given attributes (keyword arguments) if they are not None

        Args:
            entities (list[GenericEntity]): The entities to update
            **kwargs: The attributes to update with their new values

        Returns:
            list[GenericEntity]: The updated entities
        """

        session = self.get_session()
        self._emit_log("Batch updating", entities=entities, **kwargs)

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

    def get(self, entity_id: int) -> GenericEntity:
        """Retrieves an entity from the database with the specified ID.

        Args:
            entity_id (int): The ID of the entity to retrieve.

        Returns:
            GenericEntity: Object with the specified ID.

        Raises:
            EntityNotFoundException: If the entity was not found in the database
        """
        session = self.get_session()
        self._emit_log("Getting", id=entity_id)

        result = session.query(self.entity).filter(self.entity.id == entity_id).one_or_none()
        if result is None:
            raise EntityNotFoundException(f"Entity {GenericEntity.__name__} with ID {entity_id} not found")
        return result

    # pylint: disable=dangerous-default-value
    def get_batch(self, filters: Optional[list] = None) -> list[GenericEntity]:
        """Retrieves a list of entities from the database that match the specified filters.

        Args:
            filters (list): An optional list of attribute-value pairs used to filter the query. Default is an empty list.

        Returns:
            list[GenericEntity]: A list of GenericEntity objects that match the specified filters.
        """
        session = self.get_session()
        filters = filters if filters is not None else []

        # TODO: Add (MEANINGFUL!) filters to log. This is a bit tricky because filters is a list of ColumnClause objects and the type is not correctly defined within SQLModel.
        self._emit_log("Batch get")

        result = session.query(self.entity).filter(*filters).all()
        return result

    def create(self, entity: GenericEntity) -> GenericEntity:
        """Adds a new entity to the database.

        Args:
            entity (GenericEntity): A GenericEntity object to add to the database.

        Returns:
             GenericEntity: The object that was added to the database, with any auto-generated fields populated.

        Raises:
            CouldNotCreateEntityException: If there was an error inserting the entity into the database.
        """
        session = self.get_session()
        self._emit_log("Creating", entities=[entity])

        try:
            session.add(entity)
            session.commit()
            session.refresh(entity)
            return entity
        except Exception as exception:
            session.rollback()
            raise CouldNotCreateEntityException from exception

    def create_batch(self, entities: list[GenericEntity]) -> list[GenericEntity]:
        """Adds a batch of new entities to the database.

        Args:
            entities (list[GenericEntity]): A list of GenericEntity objects to add to the database.

        Returns:
            list[GenericEntity]: The objects that were added to the database, with any auto-generated fields populated.
        """
        session = self.get_session()
        self._emit_log("Batch creating", entities=entities)

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

    def delete(self, entity: GenericEntity) -> GenericEntity:
        """Deletes an entity from the database.

        Args:
            entity (GenericEntity): A GenericEntity object to delete from the database.

        Returns:
            GenericEntity: The object that was deleted from the database.

        Raises:
            DatabaseError: If there was an error deleting the entity from the database.
        """
        session = self.get_session()
        self._emit_log("Deleting", entities=[entity])

        try:
            session.delete(entity)
            session.commit()
            return entity
        except Exception as exception:
            session.rollback()
            raise CouldNotDeleteEntityException from exception

    def delete_batch(self, entities: list[GenericEntity]) -> None:
        """Deletes a batch of entities from the database.

        Args:
            entities (list[GenericEntity]): A list of GenericEntity objects to delete from the database.

        Raises:
            CouldNotDeleteEntityException: If there was an error deleting the entities from the database.
        """
        session = self.get_session()
        self._emit_log("Batch deleting", entities=entities)

        try:
            for entity in entities:
                session.delete(entity)

            session.commit()
        except Exception as exception:
            session.rollback()
            raise CouldNotDeleteEntityException from exception

    def _safe_kwargs(self, prefix: str = "", **kwargs) -> dict[str, str]:
        """Filters out sensitive attributes from the log kwargs

        Args:
            **kwargs: The key-value pairs to filter

        Returns:
            dict[str, str]: The filtered key-value pairs
        """
        excluded_keys = [*self.sensitive_attribute_keys, *self._default_excluded_keys]
        return {f"{prefix}{key}": value for key, value in kwargs.items() if key not in excluded_keys}

    def _emit_log(self, operation: str, entities: Optional[list[GenericEntity]] = None, **kwargs) -> None:
        """Emits a log message for the specified event

        Args:
            message (str): The log message to emit
            entities (Optional[list[GenericEntity]]): A list of entities to include in the log message. Default is None.
            **kwargs: Additional key-value pairs to include in the log message.
        """
        entities = entities or []
        try:
            entity_payloads = [self._safe_kwargs(**entity.dict()) for entity in entities]
            entity_log: dict = {**entity_payloads[0]} if len(entity_payloads) == 1 else {"payload": entity_payloads}
            kwargs_log: dict = self._safe_kwargs(prefix="kwarg_", **kwargs)  # Prefix is necessary to avoid conflicts with entity attributes
            self.logger.debug(f"{operation} {self.entity.__name__}", **entity_log, **kwargs_log)
        except Exception as exception:  # pylint: disable=broad-except:
            # We want to catch all exceptions here. Logs must be written by all means. It's no silent passing and thereby acceptable.
            self.logger.warning(f"Could not emit log for {operation} {self.entity.__name__}", exception=exception)  # type: ignore TODO: fix this

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
