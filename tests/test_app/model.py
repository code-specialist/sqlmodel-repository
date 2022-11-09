from enum import Enum

from sqlmodel import Relationship

from python_repository import SQLModelRepository


class PetType(Enum):
    """ Enum that describe the type of a pet """
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"


class Pet(SQLModelRepository):
    """ Pet model """
    name: str
    age: int
    type: PetType


class Shelter(SQLModelRepository):
    """ Shelter model """
    name: str
    pets: list[Pet] = Relationship(back_populates="shelter")
