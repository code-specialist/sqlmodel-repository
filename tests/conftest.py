from dataclasses import dataclass
from enum import Enum

from tests.scenario.entities import model_metadata


class Databases(Enum):
    """ Enum of the databases """
    POSTGRESQL = 'postgresql'
    SQLITE = 'sqlite'


@dataclass
class Setup:
    """ Setup for a specific database and implementation """
    database_setup: DatabaseSetup
    session_manager: SessionManager


def build_setup(database: Databases) -> Setup:
    """ Build the setups for the databases """
    database_uri = {
        Databases.POSTGRESQL: f'{POSTGRESQL_DATABASE_URI}/test',
        Databases.SQLITE: f'{SQLITE_DATABASE_URI}'
    }.get(database)

    return Setup(
        session_manager=SessionManager(database_uri=database_uri),
        database_setup=DatabaseSetup(model_metadata=model_metadata, database_uri=database_uri)
    )


setups = [build_setup(database=database) for database in Databases]


def pytest_sessionstart(_):
    """ Create or reset the databases before the tests """
    for setup in setups:
        setup.database_setup.drop_database()
        setup.database_setup.create_database()


def pytest_generate_tests(metafunc):
    """ Parametrize the tests with the database and the implementation """

    metafunc.parametrize(
        "database_session",
        [next(setup.session_manager.get_session()) for setup in setups],
        ids=["postgresql", "sqlite"]
    )
