from enum import Enum

from sqlmodel import Relationship, Field

from python_repository import SQLModelRepository


class PetType(Enum):
    """ Enum that describes the type of pet """
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"


class Pet(SQLModelRepository, table=True):
    """ Pet model """
    name: str
    age: int
    type: PetType
    shelter_id: int = Field(foreign_key="shelter.id")
    shelter: "Shelter" = Relationship(back_populates="pets")


class Shelter(SQLModelRepository, table=True):
    """ Shelter model """
    name: str
    pets: list[Pet] = Relationship(back_populates="shelter")


model_metadata = SQLModelRepository.metadata
