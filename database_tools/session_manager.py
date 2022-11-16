from __future__ import annotations

import threading
from typing import Iterator

import sqlalchemy as sqla
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import ScopedSession


class SessionManager:
    """ Manages engines, sessions and connection pools. Thread-safe singleton """

    _instance: SessionManager | None = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, database_uri: str, **kwargs):
        """ Session Manager constructor

        Args:
            database_uri (str): The URI of the database to manage sessions for

        Keyword Args:
            **kwargs: Keyword arguments to pass to the engine

            postgresql:
                pool_size (int): The maximum number of connections to the database
                max_overflow (int): The maximum number of connections to the database
                pre_ping (bool): Whether to ping the database before each connection
        """
        self._database_uri = database_uri
        self._engine = self._get_engine(**kwargs)

    @property
    def database_uri(self) -> str:
        return self._database_uri

    @property
    def engine(self) -> Engine:
        return self._engine

    def get_session(self) -> Iterator[ScopedSession]:
        """ Provides a scoped session (thread safe) that is automatically terminated by the garbage collector """
        with Session(self._engine) as session:
            yield session

    def _get_engine(self, **kwargs) -> Engine:
        """ Provides a database engine with a maximum of 20 connections and no overflows. This allows up to 20 concurrent  """
        return sqla.create_engine(
            self._database_uri,
            **kwargs
        )
