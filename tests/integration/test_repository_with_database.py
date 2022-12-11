import pytest as pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from tests.conftest import session_managers
from tests.integration.scenario.entities import Pet, Shelter, PetType
from tests.integration.scenario.repositories import PetRepository, ShelterRepository


@pytest.mark.parametrize("database_session", [next(session_manager.get_session()) for session_manager in session_managers])
class TestSQLModelRepositoryWithDatabase:

    #
    # Fixtures
    #

    @pytest.fixture
    def dog(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        dog = PetRepository.create(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        yield dog
        PetRepository.delete(entity=dog, session=database_session)

    @pytest.fixture
    def cat(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        cat = PetRepository.create(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        yield cat
        PetRepository.delete(entity=cat, session=database_session)

    @pytest.fixture
    def fish(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        fish = PetRepository.create(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)
        yield fish
        PetRepository.delete(entity=fish, session=database_session)

    @pytest.fixture
    def shelter_alpha(self, database_session: Session) -> Shelter:
        shelter = ShelterRepository.create(entity=Shelter(name="Shelter Alpha"), session=database_session)
        yield shelter
        ShelterRepository.delete(entity=shelter, session=database_session)

    @pytest.fixture
    def shelter_beta(self, database_session: Session) -> Shelter:
        shelter = ShelterRepository.create(entity=Shelter(name="Shelter Alpha"), session=database_session)
        yield shelter
        ShelterRepository.delete(entity=shelter, session=database_session)

    #
    # Tests
    #

    @staticmethod
    def test_create(database_session: Session):
        shelter = ShelterRepository.create(entity=Shelter(name="Shelter Alpha"), session=database_session)

        assert ShelterRepository.get(entity_id=shelter.id, session=database_session) == shelter

        ShelterRepository.delete(entity=shelter, session=database_session)

    @staticmethod
    def test_create_with_relation(shelter_alpha: Shelter, database_session: Session):
        cat = PetRepository.create(Pet(name='Fido', age=3, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)

        assert PetRepository.get(entity_id=cat.id, session=database_session) == cat
        assert cat.shelter == shelter_alpha

        PetRepository.delete(entity=cat, session=database_session)

    @staticmethod
    def test_get(shelter_alpha: Shelter, database_session: Session, dog: Pet):
        assert PetRepository.get(entity_id=dog.id, session=database_session) == dog

    @staticmethod
    def test_get_batch(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository.get_batch(entity_ids=[dog.id, cat.id], session=database_session)

        assert isinstance(pets, list)
        assert len(pets) == 2
        assert dog in pets
        assert cat in pets
        assert fish not in pets

    @staticmethod
    def test_get_all(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository.get_all(session=database_session)

        assert isinstance(pets, list)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets

    @staticmethod
    def test_update(shelter_alpha: Shelter, cat: Pet, database_session: Session):
        modified_cat = Pet(id=cat.id, name='Fidolina', age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)

        updated_cat = PetRepository.update(entity=cat, updates=modified_cat, session=database_session)

        assert modified_cat == updated_cat == PetRepository.get(entity_id=cat.id, session=database_session)

        PetRepository.delete(entity=cat, session=database_session)

    @staticmethod
    def test_update_by_id(shelter_alpha: Shelter, cat: Pet, database_session: Session):
        modified_cat = Pet(id=cat.id, name='Fidolina', age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)

        updated_cat = PetRepository.update_by_id(entity_id=cat.id, updates=modified_cat, session=database_session)

        assert modified_cat == updated_cat == PetRepository.get(entity_id=cat.id, session=database_session)

        PetRepository.delete(entity=cat, session=database_session)

    @staticmethod
    def test_delete(database_session: Session, dog: Pet, shelter_alpha: Shelter):
        PetRepository.delete(entity=dog, session=database_session)

        with pytest.raises(NoResultFound):
            PetRepository.get(entity_id=dog.id, session=database_session)

    @staticmethod
    def test_delete_by_id(database_session: Session, dog: Pet, shelter_alpha: Shelter):
        PetRepository.delete_by_id(entity_id=dog.id, session=database_session)

        with pytest.raises(NoResultFound):
            PetRepository.get(entity_id=dog.id, session=database_session)

    @staticmethod
    def test_delete_batch(database_session: Session, shelter_alpha: Shelter):
        dog = PetRepository.create(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        cat = PetRepository.create(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        fish = PetRepository.create(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)

        PetRepository.delete_batch(entities=[dog, cat, fish], session=database_session)

        assert PetRepository.get_batch(entity_ids=[dog.id, cat.id, fish.id], session=database_session) == []

    @staticmethod
    def test_delete_batch_by_ids(database_session: Session, shelter_alpha: Shelter):
        dog = PetRepository.create(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        cat = PetRepository.create(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        fish = PetRepository.create(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)

        PetRepository.delete_batch_by_ids(entity_ids=[dog.id, cat.id, fish.id], session=database_session)

        assert PetRepository.get_batch(entity_ids=[dog.id, cat.id, fish.id], session=database_session) == []
