import pytest

from sqlmodel_repository import SQLModelEntity


# pylint: disable=missing-class-docstring,missing-function-docstring
class TestSQLModelEntity:
    class ExampleEntity(SQLModelEntity):
        attribute: str

    @pytest.fixture
    def entity(self) -> ExampleEntity:
        return self.ExampleEntity(id=1, attribute="test_attribute")

    def test_entity_type(self, entity: ExampleEntity):
        assert isinstance(entity, self.ExampleEntity)
        assert isinstance(entity, SQLModelEntity)

    def test_entity_has_id(self, entity: ExampleEntity):
        assert hasattr(entity, "id")
        assert isinstance(entity.id, int)
