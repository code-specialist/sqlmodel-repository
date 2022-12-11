import pytest

from python_repository import SQLModelEntity


# pylint: disable=missing-class-docstring,missing-function-docstring
class TestSQLModelEntity:
    class TestEntity(SQLModelEntity):
        attribute: str

    @pytest.fixture
    def entity(self) -> TestEntity:
        return self.TestEntity(id=1, attribute="test_attribute")

    def test_entity_type(self, entity: TestEntity):
        assert isinstance(entity, self.TestEntity)
        assert isinstance(entity, SQLModelEntity)

    def test_entity_has_id(self, entity: TestEntity):
        assert hasattr(entity, "id")
        assert isinstance(entity.id, int)
