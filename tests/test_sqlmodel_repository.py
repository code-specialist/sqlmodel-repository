from sqlalchemy.orm import Session

from python_repository import RepositoryController
from tests.implementation.models import Pet
from tests.implementation.repositories import PetRepository


def test_add_pet(database_session: Session):
    """ Test adding a pet """
    pet = Pet(name='Fido', age=3, species='dog')
    PetRepository.add(session=database_session, **pet.__dict__)
