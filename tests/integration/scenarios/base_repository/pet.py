from tests.integration.scenarios.base_repository.abstract import AbstractBaseRepository
from tests.integration.scenarios.entities import Pet


class PetBaseRepository(AbstractBaseRepository[Pet]):
    """Repository to manage pets"""
