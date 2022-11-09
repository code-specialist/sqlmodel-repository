from python_repository import RepositoryController
from tests.test_app.model import Pet


class PetRepository(RepositoryController, entity=Pet):
    pass


if __name__ == '__main__':
    PetRepository.get()
