from __future__ import annotations

from typing import Type, TypeVar

from sqlalchemy.orm import Session
from sqlmodel import col

from python_repository.repository import SQLModelRepository

T = TypeVar('T')


class RepositoryController:
    """ Base class for controller implementations """
    entity: SQLModelRepository

    def __init_subclass__(cls, *args, **kwargs):
        """ Initialize subclass and set the entity that is managed by the controller """
        cls.entity: T = kwargs.get('entity')
        # TODO: Check if we create repositories for relationships here as well
        # TODO: Type hints for the entity are not working properly

    @classmethod
    def add(cls, object_to_add: Type[entity], session: Session) -> T:
        """ Add an object

        Args:
            session (Session): The session to use
            object_to_add (Type[entity]): The object to add

        Returns:
            Type[entity]: The added object instance
        """

        obj = cls.entity(**object_to_add.__dict__)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def get(cls, id: int, session: Session) -> T:
        """ Get an object by id

        Args:
            id (int): The id of the object
            session (Session): The session to use

        Returns:
            Type[entity]: The object instance

        Raises:
            NoResultFound: If no object was found
        """
        return session.query(cls.entity).filter(cls.entity.id == id).one()

    @classmethod
    def get_all(cls, session: Session) -> list[T]:
        """ Get an object by id

        Args:
            session (Session): The session to use

        Returns:
            list[Type[entity]]: The objects or an empty list if not found
        """
        return session.query(cls.entity).all()

    @classmethod
    def get_all_by_ids(cls, ids: list[int], session: Session) -> list[T]:
        """ Get an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[Type[entity]]: The objects or an empty list if not found
        """
        return session.query(cls.entity).filter(col(cls.entity.id).in_(ids)).all()

    @classmethod
    def delete(cls, id: int, session: Session) -> T:
        """ Delete an object by id

        Args:
            id (int): The id of the object
            session (Session): The session to use

        Returns:
            Type[entity]: The deleted object instance

        Raises:
            NoResultFound: If no object was found
        """
        object_to_delete = cls.get(id=id, session=session)
        session.delete(object_to_delete)
        session.commit()
        return object_to_delete

    @classmethod
    def delete_all_by_ids(cls, ids: list[int], session: Session) -> list[T]:
        """ Delete an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[Type[entity]]: The deleted objects or an empty list if no entries were affected
        """
        objects_to_delete = cls.get_all_by_ids(ids=ids, session=session)
        for to_delete in objects_to_delete:
            session.delete(to_delete)
        session.commit()
        return objects_to_delete

    @classmethod
    def update(cls, id: int, new_object: T, session: Session, allowed_attributes: list[str] = None) -> T:
        """ Update an object

        Args:
            new_object (Type[entity]): The new object
            id (int): The id of the object to updae
            session (Session): The session to use
            allowed_attributes (Optional[list[str]]): A list of attributes that are allowed to be updated. If none are provided all attributes are allowed. Defaults to None.

        Returns:
            Type[entity]: The updated object instance
        """
        object_to_update = cls.get(id=id, session=session)

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
