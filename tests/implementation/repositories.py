from python_repository import RepositoryController
from tests.implementation.models import Pet, Shelter


class PetRepository(RepositoryController, entity=Pet):
    """ Repository to manage pets """
    pass


class ShelterRepository(RepositoryController, entity=Shelter):
    """ Repository to manage shelters """
    pass
