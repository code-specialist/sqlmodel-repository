import pytest
from sqlmodel_repository.exceptions import EntityNotFoundException
from tests.integration.scenarios.base_repository.pet import PetBaseRepository
from tests.integration.scenarios.base_repository.shelter import ShelterBaseRepository
from tests.integration.scenarios.base_repository.abstract import session_manager
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

    def test_update(self, pet_base_repository: PetBaseRepository, dog: Pet):
        """Test to update an entity"""
        new_name = "Fido II"
        pet_base_repository._update(entity=dog, name=new_name)
        updated_dog = pet_base_repository._get(entity_id=dog.id)

        assert updated_dog.name == new_name
        assert updated_dog.age == dog.age
        assert updated_dog.type == dog.type
        assert updated_dog.shelter_id == dog.shelter_id

    def test_get_with_session_context(self, dog: Pet, pet_base_repository: PetBaseRepository):
        """Test to get an entity with a session context"""
        session = next(session_manager.get_session())
        _dog = pet_base_repository._get_with_session_context(entity_id=dog.id, session=session)

        assert _dog.id == dog.id
        assert _dog.name == dog.name
        assert _dog.age == dog.age
        assert _dog.type == dog.type
        assert _dog.shelter_id == dog.shelter_id

    def test_get_with_session_context_does_not_exist(self, pet_base_repository: PetBaseRepository):
        """Test to get an entity with a session context"""
        session = next(session_manager.get_session())

        with pytest.raises(EntityNotFoundException) as exception:
            pet_base_repository._get_with_session_context(entity_id=1, session=session)
            assert exception._excinfo == "Entity with id 1 not found"

    def test_get(self, dog: Pet, pet_base_repository: PetBaseRepository):
        """Test to get an entity"""
        _dog = pet_base_repository._get(entity_id=dog.id)

        assert _dog.id == dog.id
        assert _dog.name == dog.name
        assert _dog.age == dog.age
        assert _dog.type == dog.type
        assert _dog.shelter_id == dog.shelter_id

    def test_get_all(self, dog: Pet, cat: Pet, fish: Pet, pet_base_repository: PetBaseRepository):
        """Test to get all entities"""
        pets = pet_base_repository._get_all()

        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets

    def test_get_all_empty(self, pet_base_repository: PetBaseRepository):
        """Test to get all entities"""
        pets = pet_base_repository._get_all()

        assert pets == []

    def test_delete(self, pet_base_repository: PetBaseRepository, dog: Pet):
        """Test to delete an entity"""
        pet_base_repository._delete(entity=dog)
        pets = pet_base_repository._get_all()

        assert pets == []
