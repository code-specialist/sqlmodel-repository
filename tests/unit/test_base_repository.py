import pytest

from sqlmodel_repository import SQLModelEntity
from sqlmodel_repository.base_repository import BaseRepository


# pylint: disable=missing-class-docstring,missing-function-docstring,protected-access,too-few-public-methods
class TestSQLModelRepository:
    class AnotherExampleEntity(SQLModelEntity, table=True):
        attribute: str

    def test_create_repository(self):
        class TestRepository(BaseRepository[self.AnotherExampleEntity]):  # type: ignore
            pass

        assert TestRepository._entity_class() == self.AnotherExampleEntity

    @pytest.mark.parametrize("invalid_entity_class", [int, str, bool, list, BaseRepository])
    def test_create_repository_fail_invalid_entity_class(self, invalid_entity_class: type):
        class TestRepository(BaseRepository[invalid_entity_class]):  # type: ignore
            pass

        with pytest.raises(TypeError):
            TestRepository._entity_class()
