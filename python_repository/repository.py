from __future__ import annotations

from typing import TypeVar, Generic, Type, get_args

from sqlalchemy.orm import Session
from sqlmodel import col

from python_repository.entity import SQLModelEntity

GenericEntity = TypeVar('GenericEntity', SQLModelEntity, SQLModelEntity)  # must be multiple constraints


class Repository(Generic[GenericEntity]):
    """ Base class for controller implementations """

    def add(self, object_to_add: GenericEntity, session: Session) -> GenericEntity:
        """ Add an object

        Args:
            session (Session): The session to use
            object_to_add (EntityType): The object to add

        Returns:
            EntityType: The added object instance
        """
        obj = self._entity_class()(**object_to_add.__dict__)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    # noinspection PyShadowingBuiltins
    def get(self, id: int, session: Session) -> GenericEntity:
        """ Get an object by id

        Args:
            id (int): The id of the object
            session (Session): The session to use

        Returns:
            EntityType: The object instance

        Raises:
            NoResultFound: If no object was found
        """
        return session.query(self._entity_class()).filter(self._entity_class().id == id).one()

    def get_all(self, session: Session) -> list[GenericEntity]:
        """ Get an object by id

        Args:
            session (Session): The session to use

        Returns:
            list[EntityType]: The objects or an empty list if not found
        """
        return session.query(self._entity_class()).all()

    def get_all_by_ids(self, ids: list[int], session: Session) -> list[GenericEntity]:
        """ Get an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[EntityType]: The objects or an empty list if not found
        """
        return session.query(self._entity_class()).filter(col(self._entity_class().id).in_(ids)).all()

    # noinspection PyShadowingBuiltins
    def delete(self, id: int, session: Session) -> GenericEntity:
        """ Delete an object by id

        Args:
            id (int): The id of the object
            session (Session): The session to use

        Returns:
            EntityType: The deleted object instance

        Raises:
            NoResultFound: If no object was found
        """
        object_to_delete = self.get(id=id, session=session)
        session.delete(object_to_delete)
        session.commit()
        return object_to_delete

    def delete_all_by_ids(self, ids: list[int], session: Session) -> list[GenericEntity]:
        """ Delete an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[EntityType]: The deleted objects or an empty list if no entries were affected
        """
        objects_to_delete = self.get_all_by_ids(ids=ids, session=session)
        for to_delete in objects_to_delete:
            session.delete(to_delete)
        session.commit()
        return objects_to_delete

    def update(self, id: int, new_object: GenericEntity, session: Session, allowed_attributes: list[str] = None) -> GenericEntity:
        """ Update an object

        Args:
            new_object (EntityType): The new object
            id (int): The id of the object to updae
            session (Session): The session to use
            allowed_attributes (Optional[list[str]]): A list of attributes that are allowed to be updated. If none are provided all attributes are allowed. Defaults to None.

        Returns:
            EntityType: The updated object instance
        """
        object_to_update = self.get(id=id, session=session)

        if allowed_attributes is None:
            allowed_attributes = object_to_update.__dict__.keys()

        def _is_key_allowed(key: str) -> bool:
            if key in ['id', '_sa_instance_state']:
                return False
            return key in allowed_attributes

        for key, value in new_object.__dict__.items():
            if not _is_key_allowed(key):
                continue
            setattr(object_to_update, key, value)

        session.commit()
        session.refresh(object_to_update)
        return object_to_update

    def _entity_class(self) -> Type[GenericEntity]:
        """ Returns the entity class """
        # TODO: handle edge cases
        generic_type = getattr(self, '__orig_bases__')[0]
        return get_args(generic_type)[0]
