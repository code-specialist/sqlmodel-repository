import threading

import sqlalchemy as sqla
from sqlalchemy.engine import Engine
from sqlalchemy.orm import Session
from sqlalchemy.orm.scoping import ScopedSession


class SessionManager:
    """ Manages engines, sessions and connection pools. Thread-safe singleton """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            with cls._lock:
                if not cls._instance:
                    cls._instance = super(SessionManager, cls).__new__(cls)
        return cls._instance

    def __init__(self, database_uri: str, **kwargs):
        """ Session Manager constructor

        Args:
            database_uri (str): The URI of the database to manage sessions for
        """
        self.database_uri = database_uri
        self.engine = self.get_engine(**kwargs)

    def get_session(self) -> ScopedSession:
        """ Provides a scoped session (thread safe) that is automatically terminated by the garbage collector """
        with Session(self.engine) as session:
            yield session

    def get_engine(self, **kwargs) -> Engine:
        """ Provides a database engine with a maximum of 20 connections and no overflows. This allows up to 20 concurrent  """
        return sqla.create_engine(
            self.database_uri,
            **kwargs
        )
