import pytest as pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from tests.scenario.entities import Pet, Shelter, PetType
from tests.scenario.repositories import PetRepository, ShelterRepository


class TestSQLModelRepository:

    @pytest.fixture
    def dog(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        dog = PetRepository.create(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        yield dog
        PetRepository.delete(id=dog.id, session=database_session)

    @pytest.fixture
    def cat(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        cat = PetRepository.add(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        yield cat
        PetRepository.delete(id=cat.id, session=database_session)

    @pytest.fixture
    def fish(self, database_session: Session, shelter_alpha: Shelter) -> Pet:
        fish = PetRepository.add(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)
        yield fish
        PetRepository.delete(id=fish.id, session=database_session)

    @pytest.fixture
    def shelter_alpha(self, database_session: Session) -> Shelter:
        """ Test adding a shelter """
        shelter = ShelterRepository.add(Shelter(name="Shelter Alpha"), session=database_session)
        yield shelter

    @staticmethod
    def test_delete_pet(database_session: Session, shelter_alpha: Shelter):
        """ Test deleting a pet """
        dog = PetRepository.add(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        assert PetRepository.get(id=dog.id, session=database_session) == dog

        PetRepository.delete(id=dog.id, session=database_session)
        with pytest.raises(NoResultFound):
            PetRepository.get(id=dog.id, session=database_session)

    @staticmethod
    def test_delete_all_pets(database_session: Session, shelter_alpha: Shelter):
        """ Test deleting all pets """
        dog = PetRepository.add(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        cat = PetRepository.add(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        fish = PetRepository.add(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)
        assert PetRepository.delete_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session)
        assert PetRepository.get_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session) == []

    @staticmethod
    def test_add_shelter(database_session: Session):
        """ Test adding a shelter """
        shelter = ShelterRepository.add(Shelter(name="Shelter Alpha"), session=database_session)
        assert ShelterRepository.get(id=shelter.id, session=database_session) == shelter
        ShelterRepository.delete(id=shelter.id, session=database_session)

    @staticmethod
    def test_add_pet(shelter_alpha: Shelter, database_session: Session):
        """ Test adding a pet """
        cat = PetRepository.add(Pet(name='Fido', age=3, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        assert PetRepository.get(id=cat.id, session=database_session) == cat
        PetRepository.delete(id=cat.id, session=database_session)

    @staticmethod
    def test_update_pet(shelter_alpha: Shelter, database_session: Session):
        """ Test updating a pet """
        cat = PetRepository.add(Pet(name='Fido', age=3, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        assert PetRepository.get(id=cat.id, session=database_session) == cat

        modified_cat = Pet(name='Fidolina', age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)
        updated_cat = PetRepository.update(id=cat.id, new_object=modified_cat, session=database_session)

        assert updated_cat == PetRepository.get(id=cat.id, session=database_session)
        assert updated_cat.age == 12
        assert updated_cat.name == 'Fidolina'

        PetRepository.delete(id=cat.id, session=database_session)

    @staticmethod
    def test_get_all_pets(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository.get_all(session=database_session)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets

    @staticmethod
    def test_get_all_pets_by_ids(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository.get_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets
