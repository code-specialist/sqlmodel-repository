import pytest

from python_repository import SQLModelEntity, Repository


# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access,too-few-public-methods
class TestSQLModelRepository:
    class TestEntity(SQLModelEntity, table=True):
        attribute: str

    def test_create_repository(self):
        class TestRepository(Repository[self.TestEntity]):
            pass

        assert TestRepository._entity_class() == self.TestEntity

    @pytest.mark.parametrize("invalid_entity_class", [int, str, bool, list, Repository])
    def test_create_repository_fail_invalid_entity_class(self, invalid_entity_class: type):
        class TestRepository(Repository[invalid_entity_class]):
            pass

        with pytest.raises(TypeError):
            TestRepository._entity_class()
