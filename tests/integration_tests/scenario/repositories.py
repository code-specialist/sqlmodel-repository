from python_repository import Repository
from tests.integration_tests.scenario.entities import Pet, Shelter


class PetRepository(Repository[Pet]):
    """ Repository to manage pets """
    pass


class ShelterRepository(Repository[Shelter]):
    """ Repository to manage shelters """
    pass