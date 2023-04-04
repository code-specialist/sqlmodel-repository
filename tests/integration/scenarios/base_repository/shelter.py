from tests.integration.scenarios.base_repository.abstract import AbstractBaseRepository
from tests.integration.scenarios.entities import Shelter


class ShelterBaseRepository(AbstractBaseRepository[Shelter]):
    """Repository to manage shelters"""
