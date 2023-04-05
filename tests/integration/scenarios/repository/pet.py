from tests.integration.scenarios.repository.abstract import AbstractRepository
from tests.integration.scenarios.entities import Pet


class PetRepository(AbstractRepository[Pet]):
    """Repository to manage pets"""
