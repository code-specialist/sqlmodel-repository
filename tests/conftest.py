from database_setup_tools.setup import DatabaseSetup
import pytest
from tests.config import POSTGRESQL_DATABASE_URI
from tests.integration.scenarios.entities import model_metadata


def patch_database_target(monkeypatch):
    """Patch the database target to use a test database"""
    monkeypatch.setenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/test")


# pylint: disable=unused-argument
def pytest_sessionstart(session):
    """Create or reset the databases before the tests"""
    database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI)
    database_setup.drop_database()
    database_setup.create_database()


@pytest.fixture(scope="function", autouse=True)
def before_each_test():
    """Reset the database before each test"""
    # TODO: Truncating crashes the session somehow. Lets investigate this
    database_setup = DatabaseSetup(model_metadata=model_metadata, database_uri=POSTGRESQL_DATABASE_URI)
    database_setup.drop_database()
    database_setup.create_database()
    # TODO: Sometimes:
    # psycopg2.OperationalError: server closed the connection unexpectedly
    #   This probably means the server terminated abnormally
    #    before or while processing the request.
