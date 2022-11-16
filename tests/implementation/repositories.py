from python_repository import Repository
from tests.implementation.entities import Pet, Shelter


class PetRepository(Repository[Pet]):
    """ Repository to manage pets """
    pass


class ShelterRepository(Repository[Shelter]):
    """ Repository to manage shelters """
    pass