from tests.integration.scenarios.entities import Shelter
from tests.integration.scenarios.repository.abstract import AbstractRepository


class ShelterRepository(AbstractRepository[Shelter]):
    """Repository to manage shelters"""
