from typing import Generator
from unittest.mock import MagicMock
import pytest
from sqlalchemy.sql.elements import ColumnClause
from sqlmodel import col
from structlog import WriteLogger
from sqlmodel_repository.entity import SQLModelEntity
from sqlmodel_repository import BaseRepository
import json


class TestLogEntity(SQLModelEntity, table=True):
    string_attribute: str
    integer_attribute: int
    password: str


class MockBaseRepository(BaseRepository[TestLogEntity]):  # type: ignore
    def get_session(self):
        return MagicMock()


# pylint: disable=protected-access
class TestLogs:
    """Test the logging functionality of the BaseRepository class."""

    @pytest.fixture
    def base_repository(self) -> Generator[BaseRepository, None, None]:
        """Return a BaseRepository instance.""" ""
        yield MockBaseRepository(sensitive_attribute_keys=["password"])

    @pytest.fixture
    def entity(self) -> TestLogEntity:
        """Return a TestLogEntity instance."""
        return TestLogEntity(id=1, string_attribute="test_string", integer_attribute=1, password="test_password")

    def _test_attributes(self, values_to_check: dict, log_entry: dict, base_repository: BaseRepository):
        for attribute_key in values_to_check.keys():
            if attribute_key not in [*base_repository.sensitive_attribute_keys, *base_repository._default_excluded_keys]:
                assert log_entry.get(attribute_key) == values_to_check.get(attribute_key)

    def get_log_entry(self, caplog, message_beginning: str) -> dict:
        """Return the log entry for a given message beginning."""
        for record in caplog.records:
            _json = json.loads(record.message)
            if _json.get("event").startswith(message_beginning):
                return _json
        raise ValueError(f"No log entry found for message beginning: {message_beginning}")

    def test_set_logger(self):
        """Test that the logger can be set."""
        logger = WriteLogger()
        repository = MockBaseRepository(logger)
        assert repository.logger == logger

    def test_emit_log(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
        """Test that the log is emitted."""
        base_repository._emit_log("test_event", entities=[entity], **entity.dict())
        log_entry = self.get_log_entry(caplog, "test_event")
        self._test_attributes(entity.dict(), log_entry, base_repository)

    def test_emit_log_silent_raise_exception(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
        """Test that the log is emitted even if an exception is raised."""
        base_repository._emit_log("test_event", entities=["entity"])  # type: ignore
        log_entry = self.get_log_entry(caplog, f"Could not emit log for test_event {entity.__class__.__name__}")
        assert log_entry

    def test_set_sensitive_attributes(self):
        """Test that the sensitive attributes are set."""
        repository = MockBaseRepository(sensitive_attribute_keys=["password"])
        assert repository.sensitive_attribute_keys == ["password"]

    def test_get_log_kwargs_entity(self):
        """Test that the log kwargs are returned."""
        repository = MockBaseRepository(sensitive_attribute_keys=["password"])

        entity = {"id": 1, "string_attribute": "test_string", "integer_attribute": 1, "password": "test_password"}
        assert repository._safe_kwargs(**entity) == {
            "id": entity.get("id"),
            "string_attribute": entity.get("string_attribute"),
            "integer_attribute": entity.get("integer_attribute"),
        }

    def test_get_log_kwargs_entity_without_exlcuded_key(self):
        """Test that the log kwargs are returned."""
        repository = MockBaseRepository()
        entity = {"id": 1, "string_attribute": "test_string", "integer_attribute": 1, "password": "test_password"}
        assert repository._safe_kwargs(**entity) == {
            "id": entity.get("id"),
            "string_attribute": entity.get("string_attribute"),
            "integer_attribute": entity.get("integer_attribute"),
            "password": entity.get("password"),
        }

    def test_update_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that _update logs the correct information."""
        # Copy the entity attributes to check against the log entry
        values_to_check = entity.dict()

        # Update the entity
        base_repository.update(entity, string_attribute="new_string")
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Updating")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Updating {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=values_to_check, log_entry=log_entry, base_repository=base_repository)

        # Check that the kwarg is logged
        assert log_entry.get("kwarg_string_attribute") == "new_string"

    def test_update_batch_log_kwargs(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that _update_batch logs the correct information."""
        # Copy the entity attributes to check against the log entry
        values_to_check = entity.dict()

        # Update the entities
        base_repository.update_batch([entity], string_attribute="new_string")
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Batch updating")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Batch updating {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=values_to_check, log_entry=log_entry, base_repository=base_repository)

        # Check that the kwarg is logged
        assert log_entry.get("kwarg_string_attribute") == "new_string"

    def test_get_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test the the _get method logs the correct information."""
        # Get the entity
        base_repository.get(entity.id)
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Getting")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Getting {entity.__class__.__name__}"
        assert log_entry.get("kwarg_id") == entity.id

    def testget_batch_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test the the get_batch method logs the correct information."""
        # Get the entity
        base_repository.get_batch([col(TestLogEntity.id) == entity.id])
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Batch get")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Batch get {entity.__class__.__name__}"

    def test_create_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that the _create method logs the correct information."""
        # Create the entity
        base_repository.create(entity)
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Creating")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Creating {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

    def test_create_batch_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that the _create_batch method logs the correct information."""
        # Create the entity
        base_repository.create_batch([entity])
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Batch creating")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Batch creating {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

    def test_delete_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that the _delete method logs the correct information."""
        # Delete the entity
        base_repository.delete(entity)
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Deleting")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Deleting {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

    def test_delete_batch_log(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
        """Test that the _delete_batch method logs the correct information."""
        # Delete the entity
        base_repository.delete_batch([entity])
        log_entry = self.get_log_entry(caplog=caplog, message_beginning="Batch deleting")
        assert log_entry

        # Check that event is logged
        assert log_entry.get("event") == f"Batch deleting {entity.__class__.__name__}"

        # Check that the entity attributes are logged
        self._test_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)
