from enum import Enum

from database_setup_tools.session_manager import SessionManager
from database_setup_tools.setup import DatabaseSetup

from tests.config import SQLITE_DATABASE_URI
from tests.integration_tests.scenario.entities import model_metadata


class Databases(Enum):
    """ Enum of the databases """
    # POSTGRESQL = 'postgresql'
    SQLITE = 'sqlite'


def build_setup(database: Databases) -> DatabaseSetup:
    """ Build the setups for the databases """
    database_uri = {
        # Databases.POSTGRESQL: POSTGRESQL_DATABASE_URI,
        Databases.SQLITE: SQLITE_DATABASE_URI
    }.get(database)

    return DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)


setups = [build_setup(database=database) for database in Databases]
session_managers = [SessionManager(database_uri=setup.database_uri) for setup in setups]


# noinspection PyUnusedLocal
def pytest_sessionstart(session):
    """ Create or reset the databases before the tests """
    for setup in setups:
        setup.drop_database()
        setup.create_database()
