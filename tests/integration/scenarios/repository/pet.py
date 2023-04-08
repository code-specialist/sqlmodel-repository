from tests.integration.scenarios.entities import Pet
from tests.integration.scenarios.repository.abstract import AbstractRepository


class PetRepository(AbstractRepository[Pet]):
    """Repository to manage pets"""
