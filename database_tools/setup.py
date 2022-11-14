import sqlalchemy_utils
from sqlalchemy.exc import ProgrammingError

from database_tools.session_manager import SessionManager


class DatabaseSetup:
    """ Create the database and the tables if not done yet"""

    def __init__(self, model_metadata, database_uri: str):
        """ Set up a database based on its URI and metadata. Will not overwrite existing data.

        Args:
            model_metadata (TODO): The metadata of the models to create the tables for
            database_uri (str): The URI of the database to create the tables for

        """
        self.model_metadata = model_metadata
        self.database_uri = database_uri
        self.create_database()

    def create_database(self):
        """ Create the database and the tables """
        self._create_database()
        self._create_tables()

    def drop_database(self):
        """ Drop the database and the tables if possible """
        if self.database_exists:
            sqlalchemy_utils.drop_database(self.database_uri)
            return True
        return False

    @property
    def database_exists(self) -> bool:
        """ Check if the database exists """
        return sqlalchemy_utils.database_exists(self.database_uri)

    def _create_database(self):
        """ Create the database if not done yet"""
        try:
            sqlalchemy_utils.create_database(self.database_uri)
        except ProgrammingError:  # psycopg2.errors.DuplicateDatabase
            pass

    def _create_tables(self):
        """ Create the tables based on the metadata """
        session_manager = SessionManager(self.database_uri)
        engine = session_manager.get_engine()
        self.model_metadata.create_all(engine)
