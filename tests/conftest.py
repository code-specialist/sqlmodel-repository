import pytest
from database_setup_tools import DatabaseSetup

from tests.config import POSTGRESQL_DATABASE_URI
from tests.integration.scenarios.entities import Pet, Shelter, model_metadata


@pytest.fixture(scope="session")
def database_setup() -> DatabaseSetup:
    """Fixture to create a database setup"""
    return DatabaseSetup(model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI)


@pytest.fixture(scope="session")
def session_manager(database_setup: DatabaseSetup):
    """Fixture to create a session manager"""
    return database_setup.session_manager


# pylint: disable=unused-argument
def pytest_sessionstart(session):
    """Create or reset the databases before the tests"""
    database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI)
    database_setup.drop_database()
    database_setup.create_database()


@pytest.fixture(scope="function", autouse=True)
def before_each_test():
    """Reset the database before each test"""
    database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI)
    database_setup.truncate(tables=[Pet, Shelter])  # type: ignore
