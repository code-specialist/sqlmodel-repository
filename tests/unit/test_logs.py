from typing import Generator, Literal
from unittest.mock import MagicMock, patch
import json
import pytest
from sqlmodel import col
from structlog import WriteLogger
from sqlmodel_repository.entity import SQLModelEntity
from sqlmodel_repository import BaseRepository


class TestLogEntity(SQLModelEntity, table=True):
    """Test entity for logging tests."""

    string_attribute: str
    integer_attribute: int
    password: str


class MockBaseRepository(BaseRepository[TestLogEntity]):  # type: ignore
    """Mock BaseRepository for testing."""

    def get_session(self):
        return MagicMock()


def get_log_entry(caplog, message_beginning: str) -> dict:
    """Helper Method. Return the log entry for a given message beginning."""
    for record in caplog.records:
        _json = json.loads(record.message)
        if _json.get("event").startswith(message_beginning):
            return _json
    raise ValueError(f"No log entry found for message beginning: {message_beginning}")


def check_attributes(values_to_check: dict, log_entry: dict, base_repository: BaseRepository) -> Literal[True]:
    """Helper Method. Test that the log entry contains the correct values."""
    for attribute_key in values_to_check.keys():
        if attribute_key not in [*base_repository.sensitive_attribute_keys, *base_repository._default_excluded_keys]:  # pylint: disable=protected-access
            assert log_entry.get(attribute_key) == values_to_check.get(attribute_key)
    return True


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


    @pytest.fixture(autouse=True)
    def patch_get(self, request, entity: TestLogEntity):
        """Patch the get method of the BaseRepository to return the entity as we do not use am actual session."""
        if "disable_patch_get" in request.keywords:
            yield
        else:
            with patch("sqlmodel_repository.base_repository.BaseRepository.get", return_value=entity) as mock_get:
                yield mock_get

    @pytest.fixture(autouse=True)
    def patch_get_batch(self, request, entity: TestLogEntity):
        """Patch the get_batch method of the BaseRepository to return the entity as we do not use am actual session."""
        if "disable_patch_get_batch" in request.keywords:
            yield
        else:
            with patch("sqlmodel_repository.base_repository.BaseRepository.get_batch", return_value=[entity]) as mock_get_batch:
                yield mock_get_batch

    class TestClass:
        """Test the BaseRepository class"""

        def test_set_logger(self):
            """Test that the logger can be set."""
            logger = WriteLogger()
            repository = MockBaseRepository(logger)
            assert repository.logger == logger

        def test_emit_operation_begin_log(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted."""
            base_repository._emit_operation_begin_log("test_event", entities=[entity], **entity.dict())
            log_entry = get_log_entry(caplog, "test_event")
            check_attributes(entity.dict(), log_entry, base_repository)

        def test_emit_operation_success_log(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted."""
            base_repository._emit_operation_success_log("test_event", entities=[entity])
            log_entry = get_log_entry(caplog, "test_event")
            assert log_entry.get("event") == f"test_event {entity.__class__.__name__} succeeded"

        def test_emit_operation_success_log_ids(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted."""
            base_repository._emit_operation_success_log("test_event", entities=[entity])
            log_entry = get_log_entry(caplog, "test_event")
            assert log_entry.get("entity_ids") == [entity.id]

        def test_emit_operation_success_log_multiple_entities(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted."""
            base_repository._emit_operation_success_log("test_event", entities=[entity, entity])
            log_entry = get_log_entry(caplog, "test_event")
            assert log_entry.get("event") == f"test_event {entity.__class__.__name__} succeeded"

        def test_emit_operation_success_log_multiple_entities_ids(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted."""
            base_repository._emit_operation_success_log("test_event", entities=[entity, entity])
            log_entry = get_log_entry(caplog, "test_event")
            assert log_entry.get("entity_ids") == [entity.id, entity.id]

        def test_emit_log_silent_raise_exception(self, caplog, base_repository: BaseRepository, entity: TestLogEntity):
            """Test that the log is emitted even if an exception is raised."""
            base_repository._emit_operation_begin_log("test_event", entities=["entity"])  # type: ignore
            log_entry = get_log_entry(caplog, f"Could not emit log for starting test_event {entity.__class__.__name__}")
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

    class TestUpdate:
        """Test the update method."""

        class TestOperationBegin:
            """Test the begin log for the update method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that update logs the correct information."""
                # Update the entity
                base_repository.update(entity, string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Updating")

                # Check that event is logged
                assert log_entry.get("event") == f"Updating {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that update logs the entity attributes"""
                # Copy the entity attributes to check against the log entry
                values_to_check = entity.dict()

                # Update the entity
                base_repository.update(entity, string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Updating")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=values_to_check, log_entry=log_entry, base_repository=base_repository)

            def test_log_kwargs(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that update logs the keyword arguments"""
                # Update the entity
                base_repository.update(entity, string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Updating")

                # Check that the kwarg is logged
                assert log_entry.get("kwarg_string_attribute") == "new_string"

        class TestOperationSuccess:
            """Test the success log for the update method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that update logs the correct information."""
                # Update the entity
                base_repository.update(entity, string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Updating {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Updating {entity.__class__.__name__} succeeded"

            def test_ids_are_logged(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that the ids are logged."""
                # Update the entity
                base_repository.update(entity, string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Updating {entity.__class__.__name__} succeeded")

                # Check that the ids are logged
                assert log_entry.get("entity_ids") == [entity.id]

    class TestUpdateBatch:
        """Test the update_batch method."""

        class TestOperationBegin:
            """Test the begin log for the update_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _update_batch logs the correct information."""
                # Update the entities
                base_repository.update_batch([entity], string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch updating")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch updating {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _update_batch logs the correct information."""
                # Copy the entity attributes to check against the log entry
                values_to_check = entity.dict()

                # Update the entities
                base_repository.update_batch([entity], string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch updating")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=values_to_check, log_entry=log_entry, base_repository=base_repository)

            def test_log_kwargs(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _update_batch logs the correct information."""
                # Update the entities
                base_repository.update_batch([entity], string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch updating")

                # Check that the kwarg is logged
                assert log_entry.get("kwarg_string_attribute") == "new_string"

        class TestOperationSuccess:
            """Test the success log for the update_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that update logs the correct information."""
                # Update the entity
                base_repository.update_batch([entity], string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch updating {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch updating {entity.__class__.__name__} succeeded"

            def test_ids_are_logged(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that the ids are logged."""
                # Update the entity
                base_repository.update_batch([entity], string_attribute="new_string")
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch updating {entity.__class__.__name__} succeeded")

                # Check that the ids are logged
                assert log_entry.get("entity_ids") == [entity.id]

    class TestFind:
        """Test the find method."""

        class TestOperationBegin:
            """Test the begin log for the find method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _find logs the correct information."""
                # Find the entity
                base_repository.find(id=entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Finding")

                # Check that event is logged
                assert log_entry.get("event") == f"Finding {entity.__class__.__name__}"

            def test_log_kwargs(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _find logs the correct information."""
                # Find the entity
                base_repository.find(id=entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Finding")

                # Check that event is logged
                assert log_entry.get("event") == f"Finding {entity.__class__.__name__}"

            def test_log_id(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _find logs the correct information."""
                # Find the entity
                base_repository.find(id=entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Finding")

                # Check that id is logged
                assert log_entry.get("kwarg_id") == entity.id

        
        # Operation Success is covered by batch get tests
        
    class TestGet:
        """Test the get method."""

        class TestOperationBegin:
            """Tests the begin log for the get method."""

            @pytest.mark.disable_patch_get
            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _get logs the correct information."""
                # Get the entity
                base_repository.get(entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Getting")

                # Check that event is logged
                assert log_entry.get("event") == f"Getting {entity.__class__.__name__}"

            @pytest.mark.disable_patch_get
            def test_log_kwargs(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _get logs the correct information."""
                # Get the entity
                base_repository.get(entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Getting")

                assert log_entry.get("kwarg_id") == entity.id

        class TestOperationSuccess:
            """Test the success log for the get method."""

            @pytest.mark.disable_patch_get
            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that get logs the correct information."""
                # Get the entity
                base_repository.get(entity.id)
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Getting {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Getting {entity.__class__.__name__} succeeded"

            # TODO: did not find a meaningful way to test the entity id is logged, as patching seems complicated. Any ideas?

    class TestGetBatch:
        """Test the get_batch method."""

        class TestOperationBegin:
            """Test the begin log for the get_batch method."""

            @pytest.mark.disable_patch_get_batch
            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _get_batch logs the correct information."""
                # Get the entity
                base_repository.get_batch([col(TestLogEntity.id) == entity.id])
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch get")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch get {entity.__class__.__name__}"

        class TestOperationSuccess:
            """Test the success log for the get_batch method."""

            @pytest.mark.disable_patch_get_batch
            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that get_batch logs the correct information."""
                # Get the entity
                base_repository.get_batch([col(TestLogEntity.id) == entity.id])
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch get {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch get {entity.__class__.__name__} succeeded"

            # TODO: did not find a meaningful way to test the entity ids are logged, as patching seems complicated. Any ideas?

    class TestCreateLog:
        """Test the create method."""

        class TestOperationBegin:
            """Test the begin log for the create method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create logs the correct information."""
                # Create the entity
                base_repository.create(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Creating")

                # Check that event is logged
                assert log_entry.get("event") == f"Creating {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create logs the correct information."""
                # Create the entity
                base_repository.create(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Creating")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

        class TestOperationSuccess:
            """Test the success log for the create method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that create logs the correct information."""
                # Create the entity
                base_repository.create(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Creating {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Creating {entity.__class__.__name__} succeeded"

            def test_log_id(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that create logs the correct information."""
                # Create the entity
                base_repository.create(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Creating {entity.__class__.__name__} succeeded")

                # Check that the entity id is logged
                assert log_entry.get("entity_ids") == [entity.id]

    class TestCreateBatchLog:
        """Test the create_batch method."""

        class TestOperationBegin:
            """Test the begin log for the create_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create_batch logs the correct information."""
                # Create the entity
                base_repository.create_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch creating")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch creating {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create_batch logs the correct information."""
                # Create the entity
                base_repository.create_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch creating")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

        class TestOperationSuccess:
            """Test the success log for the create_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create_batch logs the correct information."""
                # Create the entity
                base_repository.create_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch creating {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch creating {entity.__class__.__name__} succeeded"

            def test_log_id(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _create_batch logs the ids"""
                # Create the entity
                base_repository.create_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch creating {entity.__class__.__name__} succeeded")

                assert log_entry.get("entity_ids") == [entity.id]

    class TestDelete:
        """Test the delete method."""

        class TestOperationBegin:
            """Test the begin log for the delete method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete logs the correct information."""
                # Delete the entity
                base_repository.delete(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Deleting")

                # Check that event is logged
                assert log_entry.get("event") == f"Deleting {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete logs the correct information."""
                # Delete the entity
                base_repository.delete(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning="Deleting")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

        class TestOperationSuccess:
            """Test the success log for the delete method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete logs the correct information."""
                # Delete the entity
                base_repository.delete(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Deleting {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Deleting {entity.__class__.__name__} succeeded"

            def test_log_id(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete logs the ids"""
                # Delete the entity
                base_repository.delete(entity)
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Deleting {entity.__class__.__name__} succeeded")

                assert log_entry.get("entity_ids") == [entity.id]

    class TestDeleteBatch:
        """Test the delete_batch method."""

        class TestOperationBegin:
            """Test the begin log for the delete_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete_batch method logs the correct information."""
                # Delete the entity
                base_repository.delete_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch deleting")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch deleting {entity.__class__.__name__}"

            def test_log_entity_attributes(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete_batch method logs the entity attributes"""
                # Delete the entity
                base_repository.delete_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning="Batch deleting")

                # Check that the entity attributes are logged
                assert check_attributes(values_to_check=entity.dict(), log_entry=log_entry, base_repository=base_repository)

        class TestOperationSuccess:
            """Test the success log for the delete_batch method."""

            def test(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete_batch method logs the correct information."""
                # Delete the entity
                base_repository.delete_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch deleting {entity.__class__.__name__} succeeded")

                # Check that event is logged
                assert log_entry.get("event") == f"Batch deleting {entity.__class__.__name__} succeeded"

            def test_log_ids(self, base_repository: BaseRepository, entity: TestLogEntity, caplog):
                """Test that _delete logs the ids"""
                # Delete the entity
                base_repository.delete_batch([entity])
                log_entry = get_log_entry(caplog=caplog, message_beginning=f"Batch deleting {entity.__class__.__name__} succeeded")

                assert log_entry.get("entity_ids") == [entity.id]
