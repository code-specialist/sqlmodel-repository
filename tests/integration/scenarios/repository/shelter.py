from tests.integration.scenarios.repository.abstract import AbstractRepository
from tests.integration.scenarios.entities import Shelter


class ShelterRepository(AbstractRepository[Shelter]):
    """Repository to manage shelters"""
