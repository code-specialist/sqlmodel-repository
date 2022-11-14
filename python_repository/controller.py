from __future__ import annotations

from typing import Type

from sqlalchemy.orm import Session

from python_repository.repository import SQLModelRepository


class RepositoryController:
    """ Base class for controller implementations """
    entity: SQLModelRepository

    def __init_subclass__(cls, *args, **kwargs):
        """ Initialize subclass and set the entity that is managed by the controller """
        cls.entity = kwargs.get('entity')

    @classmethod
    def add(cls, session: Session, **kwargs) -> Type[entity]:
        """ Add an object

        Args:
            session (Session): The session to use
            **kwargs: The attributes to set

        Returns:
            Self: The added object instance
        """
        obj = cls.entity(**kwargs)
        session.add(obj)
        session.commit()
        session.refresh(obj)
        return obj

    @classmethod
    def get(cls, id: int, session: Session) -> Type[entity]:
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
    def get_all(cls, ids: list[int], session: Session) -> list[Type[entity]]:
        """ Get an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[Type[entity]]: The objects or an empty list if not found
        """
        # in_ is a SQLAlchemy function
        # noinspection PyUnresolvedReferences
        return session.query(cls).filter(cls.entity.id.in_(ids)).all()

    @classmethod
    def delete(cls, id: int, session: Session) -> Type[entity]:
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
    def delete_all(cls, ids: list[int], session: Session) -> list[Type[entity]]:
        """ Delete an object by id

        Args:
            ids (list[int]): The ids of the objects
            session (Session): The session to use

        Returns:
            list[Type[entity]]: The deleted objects or an empty list if no entries were affected
        """
        objects_to_delete = cls.get_all(ids=ids, session=session)
        map(lambda obj: obj.delete(session), objects_to_delete)
        session.commit()
        return objects_to_delete

    @classmethod
    def update(cls, object_to_update: Type[entity], new_object: Type[entity], session: Session, allowed_attributes: list[str] = None) -> Type[entity]:
        """ Update an object

        Args:
            new_object (Type[entity]): The new object
            object_to_update (Type[entity]): The object to update
            session (Session): The session to use
            allowed_attributes (Optional[list[str]]): A list of attributes that are allowed to be updated. If none are provided all attributes are allowed. Defaults to None.

        Returns:
            Type[entity]: The updated object instance
        """
        if allowed_attributes is None:
            allowed_attributes = object_to_update.__dict__.keys()

        def _is_key_allowed(key: str) -> bool:
            return key in allowed_attributes

        for key, value in new_object.__dict__.items():
            if not _is_key_allowed(key):
                continue
            setattr(object_to_update, key, value)

        session.commit()
        session.refresh(object_to_update)
        return object_to_update
