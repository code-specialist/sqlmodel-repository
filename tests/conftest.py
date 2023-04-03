from database_setup_tools.setup import DatabaseSetup

from tests.config import POSTGRESQL_DATABASE_URI
from tests.integration.scenario.entities import model_metadata


class RepositoryTest:
    pass


# pylint: disable=unused-argument
# noinspection PyUnusedLocal
def pytest_sessionstart(session):
    """Create or reset the databases before the tests"""
    setup = DatabaseSetup(
        model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI
    )  # TODO: This is fucked up. The DB Setup fails once the db exists because it creates it by default.
    setup.drop_database()
    setup.create_database()
