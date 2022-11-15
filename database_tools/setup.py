import sqlalchemy_utils

from database_tools.session_manager import SessionManager


class DatabaseSetup:
    """ Create the database and the tables if not done yet"""

    def __init__(self, model_metadata, database_uri: str):
        """ Set up a database based on its URI and metadata. Will not overwrite existing data.

        Args:
            model_metadata (TODO): The metadata of the models to create the tables for
            database_uri (str): The URI of the database to create the tables for

        """
        self._model_metadata = model_metadata
        self._database_uri = database_uri
        self.create_database()

    def create_database(self) -> None:
        """ Create the database and the tables """
        self._create_database()
        self._create_tables()

    def drop_database(self) -> None:
        """ Drop the database and the tables if possible """
        if self.database_exists:
            sqlalchemy_utils.drop_database(self._database_uri)

    @property
    def database_uri(self) -> str:
        return self._database_uri

    @property
    def database_exists(self) -> bool:
        """ Check if the database exists """
        return sqlalchemy_utils.database_exists(self._database_uri)

    def _create_database(self) -> None:
        """ Create the database if not done yet"""
        if not self.database_exists:
            sqlalchemy_utils.create_database(self._database_uri)

    def _create_tables(self) -> None:
        """ Create the tables based on the metadata """
        session_manager = SessionManager(self._database_uri)
        self._model_metadata.create_all(session_manager.engine)
