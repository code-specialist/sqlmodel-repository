import pytest as pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from tests.implementation.entities import Pet, Shelter, PetType
from tests.implementation.repositories import PetRepository, ShelterRepository


class TestSQLModelRepository:

    @pytest.fixture
    def pet_repository(self) -> PetRepository:
        return PetRepository()

    @pytest.fixture
    def shelter_repository(self) -> ShelterRepository:
        return ShelterRepository()

    @pytest.fixture
    def dog(self, database_session: Session, shelter_alpha: Shelter, pet_repository: PetRepository) -> Pet:
        dog = pet_repository.add(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        yield dog
        pet_repository.delete(id=dog.id, session=database_session)

    @pytest.fixture
    def cat(self, database_session: Session, shelter_alpha: Shelter, pet_repository: PetRepository) -> Pet:
        cat = pet_repository.add(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        yield cat
        pet_repository.delete(id=cat.id, session=database_session)

    @pytest.fixture
    def fish(self, database_session: Session, shelter_alpha: Shelter, pet_repository: PetRepository) -> Pet:
        fish = pet_repository.add(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)
        yield fish
        pet_repository.delete(id=fish.id, session=database_session)

    @pytest.fixture
    def shelter_alpha(self, database_session: Session, shelter_repository: ShelterRepository) -> Shelter:
        """ Test adding a shelter """
        shelter = shelter_repository.add(Shelter(name="Shelter Alpha"), session=database_session)
        yield shelter

    @staticmethod
    def test_delete_pet(database_session: Session, shelter_alpha: Shelter, pet_repository: PetRepository):
        """ Test deleting a pet """
        dog = pet_repository.add(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        assert pet_repository.get(id=dog.id, session=database_session) == dog

        pet_repository.delete(id=dog.id, session=database_session)
        with pytest.raises(NoResultFound):
            pet_repository.get(id=dog.id, session=database_session)

    @staticmethod
    def test_delete_all_pets(database_session: Session, shelter_alpha: Shelter, pet_repository: PetRepository):
        """ Test deleting all pets """
        dog = pet_repository.add(Pet(name='Fido', age=3, type=PetType.DOG, shelter_id=shelter_alpha.id), session=database_session)
        cat = pet_repository.add(Pet(name='Felix', age=2, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        fish = pet_repository.add(Pet(name='Nemo', age=1, type=PetType.FISH, shelter_id=shelter_alpha.id), session=database_session)
        assert pet_repository.delete_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session)
        assert pet_repository.get_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session) == []

    @staticmethod
    def test_add_shelter(database_session: Session, shelter_repository: ShelterRepository):
        """ Test adding a shelter """
        shelter = shelter_repository.add(Shelter(name="Shelter Alpha"), session=database_session)
        assert shelter_repository.get(id=shelter.id, session=database_session) == shelter
        shelter_repository.delete(id=shelter.id, session=database_session)

    @staticmethod
    def test_add_pet(shelter_alpha: Shelter, database_session: Session, pet_repository: PetRepository):
        """ Test adding a pet """
        cat = pet_repository.add(Pet(name='Fido', age=3, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        assert pet_repository.get(id=cat.id, session=database_session) == cat
        pet_repository.delete(id=cat.id, session=database_session)

    @staticmethod
    def test_update_pet(shelter_alpha: Shelter, database_session: Session, pet_repository: PetRepository):
        """ Test updating a pet """
        cat = pet_repository.add(Pet(name='Fido', age=3, type=PetType.CAT, shelter_id=shelter_alpha.id), session=database_session)
        assert pet_repository.get(id=cat.id, session=database_session) == cat

        modified_cat = Pet(name='Fidolina', age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)
        updated_cat = pet_repository.update(id=cat.id, new_object=modified_cat, session=database_session)

        assert updated_cat == pet_repository.get(id=cat.id, session=database_session)
        assert updated_cat.age == 12
        assert updated_cat.name == 'Fidolina'

        pet_repository.delete(id=cat.id, session=database_session)

    @staticmethod
    def test_get_all_pets(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet, pet_repository: PetRepository):
        pets = pet_repository.get_all(session=database_session)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets

    @staticmethod
    def test_get_all_pets_by_ids(shelter_alpha: Shelter, database_session: Session, dog: Pet, cat: Pet, fish: Pet, pet_repository: PetRepository):
        pets = pet_repository.get_all_by_ids(ids=[dog.id, cat.id, fish.id], session=database_session)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets
