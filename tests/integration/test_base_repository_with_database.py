import pytest
from sqlmodel_repository.exceptions import CouldNotDeleteEntityException, EntityNotFoundException
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
    def dog(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a dog"""
        _dog = pet_base_repository._create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        return _dog

    @pytest.fixture
    def cat(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a cat"""
        _cat = pet_base_repository._create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        return _cat

    @pytest.fixture
    def fish(self, pet_base_repository: PetBaseRepository, shelter_alpha: Shelter) -> Pet:
        """Fixture to create a fish"""
        _fish = pet_base_repository._create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))
        return _fish

    @pytest.fixture
    def shelter_alpha(self, shelter_base_repository: ShelterBaseRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_base_repository._create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_beta(self, shelter_base_repository: ShelterBaseRepository) -> Shelter:
        """Fixture to create a shelter"""
        _shelter = shelter_base_repository._create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_base_repository(self) -> ShelterBaseRepository:
        """Fixture to create a shelter repository. Fake Dependency Injection."""
        return ShelterBaseRepository()

    @pytest.fixture
    def pet_base_repository(self) -> PetBaseRepository:
        """Fixture to create a pet repository. Fake Dependency Injection."""
        return PetBaseRepository()

    #
    # Tests
    #

    class TestUpdate:
        """Tests for the _update method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to update an entity"""
            new_name = "Fido II"
            pet_base_repository._update(entity=dog, name=new_name)
            updated_dog = pet_base_repository._get(entity_id=dog.id)

            assert updated_dog.name == new_name
            assert updated_dog.age == dog.age
            assert updated_dog.type == dog.type
            assert updated_dog.shelter_id == dog.shelter_id

        @staticmethod
        def test_raise_entity_not_found(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to update an entity fails if the entity does not exist"""
            pet_base_repository._delete(entity=dog)

            with pytest.raises(EntityNotFoundException):
                pet_base_repository._update(entity=dog, name="new_name")  # type: ignore

    class TestGet:
        """Tests for the _get method"""

        @staticmethod
        def test(dog: Pet, pet_base_repository: PetBaseRepository):
            """Test to get an entity"""
            _dog = pet_base_repository._get(entity_id=dog.id)

            assert _dog.id == dog.id
            assert _dog.name == dog.name
            assert _dog.age == dog.age
            assert _dog.type == dog.type
            assert _dog.shelter_id == dog.shelter_id

    class TestGetAll:
        """Tests for the _get_all method"""

        @staticmethod
        def test(dog: Pet, cat: Pet, fish: Pet, pet_base_repository: PetBaseRepository):
            """Test to get all entities"""
            pets = pet_base_repository._get_all()

            assert len(pets) == 3
            assert dog in pets
            assert cat in pets
            assert fish in pets

        @staticmethod
        def test_empty(pet_base_repository: PetBaseRepository):
            """Test to get all entities"""
            pets = pet_base_repository._get_all()

            assert pets == []

    class TestDelete:
        """Tests for the _delete method"""

        @staticmethod
        def test(pet_base_repository: PetBaseRepository, dog: Pet):
            """Test to delete an entity"""
            pet_base_repository._delete(entity=dog)
            pets = pet_base_repository._get_all()

            assert pets == []

        @staticmethod
        def test_raise_could_not_delete_entity(pet_base_repository: PetBaseRepository, dog: Pet):  # pylint: disable=unused-argument
            """Test to delete an entity"""
            with pytest.raises(CouldNotDeleteEntityException):
                pet_base_repository._delete(entity="dog")  # type: ignore
