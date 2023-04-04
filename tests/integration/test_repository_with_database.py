from typing import Generator

import pytest
from sqlalchemy.exc import NoResultFound
from sqlalchemy.orm import Session

from tests.conftest import RepositoryTest
from tests.integration.scenario.entities import Pet, PetType, Shelter
from tests.integration.scenario.repositories import PetRepository, ShelterRepository


class TestSQLModelRepositoryWithDatabase(RepositoryTest):

    #
    # Fixtures
    #

    @pytest.fixture
    def dog(self, shelter_alpha: Shelter) -> Pet:
        _dog = PetRepository().create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        return _dog

    @pytest.fixture
    def cat(self, shelter_alpha: Shelter) -> Pet:
        _cat = PetRepository().create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        return _cat

    @pytest.fixture
    def fish(self, shelter_alpha: Shelter) -> Pet:
        _fish = PetRepository().create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))
        return _fish

    @pytest.fixture
    def shelter_alpha(self) -> Shelter:
        _shelter = ShelterRepository().create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    @pytest.fixture
    def shelter_beta(self) -> Shelter:
        _shelter = ShelterRepository().create(entity=Shelter(name="Shelter Alpha"))
        return _shelter

    #
    # Tests
    #

    @staticmethod
    def test_create():
        shelter = ShelterRepository().create(entity=Shelter(name="Shelter Alpha"))

        assert ShelterRepository().get(entity_id=shelter.id) == shelter

        ShelterRepository().delete(entity=shelter)

    @staticmethod
    def test_create_with_relation(shelter_alpha: Shelter):
        cat = PetRepository().create(Pet(name="Fido", age=3, type=PetType.CAT, shelter_id=shelter_alpha.id))

        assert PetRepository().get(entity_id=cat.id) == cat
        assert cat.shelter == shelter_alpha

        PetRepository().delete(entity=cat)

    @staticmethod
    def test_get(dog: Pet):
        assert PetRepository().get(entity_id=dog.id) == dog

    @staticmethod
    def test_get_batch(dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository().get_batch(entity_ids=[dog.id, cat.id])

        assert isinstance(pets, list)
        assert len(pets) == 2
        assert dog in pets
        assert cat in pets
        assert fish not in pets

    @staticmethod
    def test_get_all(dog: Pet, cat: Pet, fish: Pet):
        pets = PetRepository().get_all()

        assert isinstance(pets, list)
        assert len(pets) == 3
        assert dog in pets
        assert cat in pets
        assert fish in pets

    @staticmethod
    def test_update(shelter_alpha: Shelter, cat: Pet):
        modified_cat = Pet(id=cat.id, name="Fidolina", age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)

        updated_cat = PetRepository().update(entity=cat, updates=modified_cat)

        assert modified_cat == updated_cat == PetRepository().get(entity_id=cat.id)

        PetRepository().delete(entity=cat)

    @staticmethod
    def test_update_by_id(shelter_alpha: Shelter, cat: Pet):
        modified_cat = Pet(id=cat.id, name="Fidolina", age=12, type=PetType.CAT, shelter_id=shelter_alpha.id)

        updated_cat = PetRepository().update_by_id(entity_id=cat.id, updates=modified_cat)

        assert modified_cat == updated_cat == PetRepository().get(entity_id=cat.id)

        PetRepository().delete(entity=cat)

    @staticmethod
    def test_delete(dog: Pet):
        PetRepository().delete(entity=dog)

        with pytest.raises(NoResultFound):
            PetRepository().get(entity_id=dog.id)

    @staticmethod
    def test_delete_by_id(dog: Pet):
        PetRepository().delete_by_id(entity_id=dog.id)

        with pytest.raises(NoResultFound):
            PetRepository().get(entity_id=dog.id)

    @staticmethod
    def test_delete_batch(shelter_alpha: Shelter):
        dog = PetRepository().create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        cat = PetRepository().create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        fish = PetRepository().create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))

        PetRepository().delete_batch(entities=[dog, cat, fish])

        assert PetRepository().get_batch(entity_ids=[dog.id, cat.id, fish.id]) == []

    @staticmethod
    def test_delete_batch_by_ids(shelter_alpha: Shelter):
        dog = PetRepository().create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=shelter_alpha.id))
        cat = PetRepository().create(Pet(name="Felix", age=2, type=PetType.CAT, shelter_id=shelter_alpha.id))
        fish = PetRepository().create(Pet(name="Nemo", age=1, type=PetType.FISH, shelter_id=shelter_alpha.id))

        PetRepository().delete_batch_by_ids(entity_ids=[dog.id, cat.id, fish.id])

        assert PetRepository().get_batch(entity_ids=[dog.id, cat.id, fish.id]) == []
