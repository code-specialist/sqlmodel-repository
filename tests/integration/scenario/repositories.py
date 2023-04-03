from python_repository import Repository
from tests.integration.scenario.entities import Pet, Shelter


class PetRepository(Repository[Pet]):
    """Repository to manage pets"""


class ShelterRepository(Repository[Shelter]):
    """Repository to manage shelters"""
