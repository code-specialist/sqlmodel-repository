from typing import Generator

import pytest
from database_setup_tools import SessionManager
from sqlalchemy.orm import Session

from sqlmodel_repository.exceptions import CouldNotCreateEntityException, CouldNotDeleteEntityException, EntityDoesNotPossessAttributeException, EntityNotFoundException
from tests.integration.scenarios.base_repository.pet import PetBaseRepository
from tests.integration.scenarios.base_repository.shelter import ShelterBaseRepository
from tests.integration.scenarios.entities import Pet, PetType, Shelter


# pylint: disable=protected-access
class TestBaseRepositoryWithDatabase:
    """Integration tests for the BaseRepository class."""

    #
    # Fixtures
    #

    @pytest.fixture
    def session(self, session_manager: SessionManager) -> Generator[Session, None, None]:
        session = next(session_manager.get_session())
        yield session
        session.close()

    @pytest.fixture
    def dog(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a dog"""
        _dog = pet_base_repository.create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        return _dog

    @pytest.fixture
    def cat(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a cat"""
        _cat = pet_base_repository.create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        return _cat

    @pytest.fixture
    def fish(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a fish"""
        _fish = pet_base_repository.create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))
        return _fish

    @pytest.fixture
    def shelter_alpha(self, shelter_base_repository: ShelterBaseRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_base_repository.create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_beta(self, shelter_base_repository: ShelterBaseRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_base_repository.create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_base_repository(self, session: Session) -> ShelterBaseRepository:
        """Fixture to create a shelter repository. Fake Dependency Injection."""
        return ShelterBaseRepository(session)

    @pytest.fixture
    def pet_base_repository(self, session: Session) -> PetBaseRepository:
        """Fixture to create a pet repository. Fake Dependency Injection."""
        return PetBaseRepository(session)

    #
    # Tests
    #

    class TestCreate:
        """Tests for the _create method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, shelter_alpha: Shelter):
            """Test to create an entity"""
            entity = Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id)
            fido = pet_base_repository.create(entity=entity)

            _fido = pet_base_repository.get(entity_id=fido.id)

            assert _fido == fido

        @staticmethod
        def test_id_is_populated(pet_base_repository: PetBaseRepository, shelter_alpha: Shelter):
            """Test to create an entity"""
            entity = Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id)
            pet_base_repository.create(entity=entity)

            assert entity.id is not None

    class TestFind:
        """Tests for the find method."""

        def test_find_one_by_attribute(self, pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to find an entity"""
            assert pet_base_repository.find(name=dog.name) == [dog]
            assert pet_base_repository.find(type=PetType.DOG) == [dog]

        def test_find_all_by_attribute(self, pet_base_repository: PetBaseRepository, dog: Pet, cat: Pet, fish: Pet, shelter_alpha: Shelter, shelter_beta: Shelter):
            """Test to find an entity"""
            assert pet_base_repository.find(shelter=shelter_alpha) == [dog, cat, fish]

        def test_raises_entity_does_not_possess_attribute(self, pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to find an entity"""
            with pytest.raises(EntityDoesNotPossessAttributeException):
                pet_base_repository.find(legs=12)

    class TestFindOne:
        """Tests for the find_one method."""

        def test_find_one_by_attribute(self, pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to find an entity"""
            assert pet_base_repository.find_one(name=dog.name) == dog
            assert pet_base_repository.find_one(type=PetType.DOG) == dog

        def test_raises_entity_does_not_possess_attribute(self, pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to find an entity"""
            with pytest.raises(EntityDoesNotPossessAttributeException):
                pet_base_repository.find_one(legs=12)

    class TestCreateBatch:
        """Tests for the _create_batch method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, shelter_alpha: Shelter):
            """Test to create a batch of entities"""
            pets = [
                Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id),
                Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id),
                Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id),
            ]
            pet_base_repository.create_batch(entities=pets)
            assert pet_base_repository.get_batch() == pets

        @staticmethod
        def test_attributes_are_populated(pet_base_repository: PetBaseRepository, shelter_alpha: Shelter):
            """Test to create a batch of entities"""
            pets = [
                Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id),
                Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id),
                Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id),
            ]
            pets = pet_base_repository.create_batch(entities=pets)

            for pet in pets:
                assert pet.id is not None

        @staticmethod
        def test_raises_could_not_create_entity(pet_base_repository: PetBaseRepository, shelter_alpha: Shelter):
            """Test to create a batch of entities and raise an exception"""
            pets = [
                "Hans der Tepppichwal",
                Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id),
                Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id),
            ]
            with pytest.raises(CouldNotCreateEntityException):
                pet_base_repository.create_batch(entities=pets)

    class TestUpdate:
        """Tests for the _update method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to update an entity"""
            new_name = "Fido II"
            pet_base_repository.update(entity=dog, name=new_name)
            updated_dog = pet_base_repository.get(entity_id=dog.id)

            assert updated_dog.name == new_name
            assert updated_dog.age == dog.age
            assert updated_dog.type == dog.type
            assert updated_dog.shelter_id == dog.shelter_id

        @staticmethod
        def test_raise_entity_not_found(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to update an entity fails if the entity does not exist"""
            pet_base_repository.delete(entity=dog)

            with pytest.raises(EntityNotFoundException):
                pet_base_repository.update(entity=dog, name="new_name")  # type: ignore

        @staticmethod
        def test_raises_entity_does_not_possess_attribute(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to update an entity fails if the entity does not possess the attribute"""
            with pytest.raises(EntityDoesNotPossessAttributeException):
                pet_base_repository.update(entity=dog, name="new_name", age=10, type=PetType.CAT, shelter_id=1, unknown_attribute="unknown")

    class TestUpdateBatch:
        """Tests for the _update_batch method"""

        def test(self, pet_base_repository: PetBaseRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to update an entity"""
            new_name = "Fido II"
            pet_base_repository.update_batch(entities=[dog, cat, fish], name=new_name)
            updated_dog = pet_base_repository.get(entity_id=dog.id)
            updated_cat = pet_base_repository.get(entity_id=cat.id)
            updated_fish = pet_base_repository.get(entity_id=fish.id)

            assert updated_dog.name == new_name
            assert updated_dog.age == dog.age
            assert updated_dog.type == dog.type
            assert updated_dog.shelter_id == dog.shelter_id

            assert updated_cat.name == new_name
            assert updated_cat.age == cat.age
            assert updated_cat.type == cat.type
            assert updated_cat.shelter_id == cat.shelter_id

            assert updated_fish.name == new_name
            assert updated_fish.age == fish.age
            assert updated_fish.type == fish.type
            assert updated_fish.shelter_id == fish.shelter_id

    class TestGet:
        """Tests for the _get method"""

        @staticmethod
        def test(dog: Pet, pet_base_repository: PetBaseRepository):
            """Test to get an entity"""
            _dog = pet_base_repository.get(entity_id=dog.id)

            assert _dog.id == dog.id
            assert _dog.name == dog.name
            assert _dog.age == dog.age
            assert _dog.type == dog.type
            assert _dog.shelter_id == dog.shelter_id

        @staticmethod
        def test_relationship_attribute(dog: Pet, pet_base_repository: PetBaseRepository):
            """Test to get an entity"""
            _dog = pet_base_repository.get(entity_id=dog.id)

            assert _dog.id == dog.id
            assert _dog.name == dog.name
            assert _dog.age == dog.age
            assert _dog.type == dog.type
            assert _dog.shelter_id == dog.shelter_id

            assert _dog.shelter == dog.shelter  # Fails due to "DetachedInstanceError: Parent instance <Pet at 0x10826a840> is not bound to a Session" (dog instance)

    class TestGetBatch:
        """Tests for the get_batch method"""

        @staticmethod
        def test(dog: Pet, cat: Pet, fish: Pet, pet_base_repository: PetBaseRepository):
            """Test to get all entities"""
            pets = pet_base_repository.get_batch()

            assert len(pets) == 3
            assert dog in pets
            assert cat in pets
            assert fish in pets

        @staticmethod
        def test_empty(pet_base_repository: PetBaseRepository):
            """Test to get all entities"""
            pets = pet_base_repository.get_batch()

            assert pets == []

    class TestDelete:
        """Tests for the _delete method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to delete an entity"""
            pet_base_repository.delete(entity=dog)
            pets = pet_base_repository.get_batch()

            assert pets == []

        @staticmethod
        def test_raise_could_not_delete_entity(pet_base_repository: PetBaseRepository, dog: Pet):  # pylint: disable=unused-argument
            """Test to delete an entity"""
            with pytest.raises(CouldNotDeleteEntityException):
                pet_base_repository.delete(entity="dog")  # type: ignore

    class TestDeleteBatch:
        """Tests for the _delete_batch method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to delete an entity"""
            pet_base_repository.delete_batch(entities=[dog, cat, fish])
            pets = pet_base_repository.get_batch()

            assert pets == []

        @staticmethod
        def test_raise_could_not_delete_entity(pet_base_repository: PetBaseRepository, dog: Pet, cat: Pet, fish: Pet):
            """Test to delete an entity fails if the entity does not exist"""
            with pytest.raises(CouldNotDeleteEntityException):
                pet_base_repository.delete_batch(entities=["dog", cat, fish])  # type: ignore
