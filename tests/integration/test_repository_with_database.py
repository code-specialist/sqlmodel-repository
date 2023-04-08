from typing import Generator
from database_setup_tools.session_manager import SessionManager
import pytest
from sqlalchemy.orm import Session
from sqlmodel_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityNotFoundException

from tests.integration.scenarios.entities import Pet, PetType, Shelter
from tests.integration.scenarios.repository.pet import PetRepository
from tests.integration.scenarios.repository.shelter import ShelterRepository


class TestRepositoryWithDatabase:
    """Integration tests for the Repository class."""

    #
    # Fixtures
    #

    @pytest.fixture
    def session(self, session_manager: SessionManager) -> Generator[Session, None, None]:
        session = next(session_manager.get_session())
        yield session
        session.close()

    @pytest.fixture
    def dog(self, pet_repository: PetRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a dog"""
        _dog = pet_repository.create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        return _dog

    @pytest.fixture
    def cat(self, pet_repository: PetRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a cat"""
        _cat = pet_repository.create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        return _cat

    @pytest.fixture
    def fish(self, pet_repository: PetRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a fish"""
        _fish = pet_repository.create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))
        return _fish

    @pytest.fixture
    def shelter_alpha(self, shelter_repository: ShelterRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_repository.create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_beta(self, shelter_repository: ShelterRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_repository.create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_repository(self, session: Session) -> ShelterRepository:
        """Fixture to create a shelter repository. Fake Dependency Injection."""
        return ShelterRepository(session)

    @pytest.fixture
    def pet_repository(self, session: Session) -> PetRepository:
        """Fixture to create a pet repository. Fake Dependency Injection."""
        return PetRepository(session)

    #
    # Tests
    #
    class TestGet:
        """Tests for the get method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet):
            """Test to get an entity"""
            assert pet_repository.get(entity_id=dog.id) == dog

        @staticmethod
        def test_raise_entity_not_found(pet_repository: PetRepository):
            """Test to get an entity that does not exist"""
            with pytest.raises(EntityNotFoundException):
                pet_repository.get(entity_id=1)

    class TestCreate:
        """Tests for the create method."""

        @staticmethod
        def test(shelter_repository: ShelterRepository):
            """Test to create a new entity"""
            shelter = shelter_repository.create(entity=Shelter(name="Shelter Alpha"))
            assert shelter_repository.get(entity_id=shelter.id) == shelter

        @staticmethod
        def test_raise_could_not_create_entity(shelter_repository: ShelterRepository):
            """Test to create a new entity that raises the CouldNotCreateEntityException"""
            with pytest.raises(CouldNotCreateEntityException):
                shelter_repository.create(entity="Hans Peter the Goldfish")  # type: ignore

    class TestGetBatch:
        """Tests for the get_batch method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to get a batch of entities"""
            pets = pet_repository.get_batch(entity_ids=[dog.id, cat.id])

            assert isinstance(pets, list)
            assert len(pets) == 2
            assert dog in pets
            assert cat in pets
            assert fish not in pets

        @staticmethod
        def test_empty_ids(pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to get a batch of entities"""
            pets = pet_repository.get_batch(entity_ids=[])

            assert len(pets) == 0
            assert dog not in pets
            assert cat not in pets
            assert fish not in pets

    class TestGetAll:
        """Tests for the get_all method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to get all entities"""
            pets = pet_repository.get_all()

            assert isinstance(pets, list)
            assert len(pets) == 3
            assert dog in pets
            assert cat in pets
            assert fish in pets

    class TestUpdate:
        """Tests for the update method."""

        @staticmethod
        def test(pet_repository: PetRepository, cat: Pet):
            """Test to update an entity"""
            updated_cat = pet_repository.update(entity=cat, name="Fidolina", age=12)
            assert updated_cat == pet_repository.get(entity_id=cat.id)

    class TestUpdateById:
        """Tests for the update_by_id method."""

        @staticmethod
        def test(pet_repository: PetRepository, cat: Pet):
            """Test to update an entity by id"""
            updated_cat = pet_repository.update_by_id(entity_id=cat.id, name="Fidolina", age=12)
            assert updated_cat == pet_repository.get(entity_id=cat.id)

    class TestDelete:
        """Tests for the delete method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet):
            """Test to delete an entity"""
            pet_repository.delete(entity=dog)
            with pytest.raises(EntityNotFoundException):
                pet_repository.get(entity_id=dog.id)

        @staticmethod
        def test_with_cascade(shelter_repository: ShelterRepository, shelter_alpha: Shelter, pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to delete an entity"""
            shelter_repository.delete(entity=shelter_alpha)

            # Ensure that all pets are deleted as well
            for pet in [dog, cat, fish]:
                with pytest.raises(EntityNotFoundException):
                    pet_repository.get(entity_id=pet.id)

        @staticmethod
        def test_raise_could_not_delete_entity(pet_repository: PetRepository):
            """Test to delete an entity"""
            with pytest.raises(CouldNotDeleteEntityException):
                pet_repository.delete(entity="Gundula the Tarantula")  # type: ignore

    class TestDeleteById:
        """Tests for the delete_by_id method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet):
            """Test to delete an entity by id"""
            pet_repository.delete_by_id(entity_id=dog.id)
            with pytest.raises(EntityNotFoundException) as exception:
                pet_repository.get(entity_id=dog.id)
                assert exception._excinfo == f"Entity with id {dog.id} not found"  # pylint: disable=protected-access

    class TestDeleteBatch:
        """Tests for the delete_batch method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to delete a batch of entities"""
            pet_repository.delete_batch(entities=[dog, cat, fish])
            assert pet_repository.get_batch(entity_ids=[dog.id, cat.id, fish.id]) == []

    class TestDeleteBatchByIds:
        """Tests for the delete_batch_by_ids method."""

        @staticmethod
        def test(pet_repository: PetRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to delete a batch of entities by ids"""
            pet_repository.delete_batch_by_ids(entity_ids=[dog.id, cat.id, fish.id])
            assert pet_repository.get_batch(entity_ids=[dog.id, cat.id, fish.id]) == []
