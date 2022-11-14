from enum import Enum

from python_repository import SQLModelRepository
from sqlmodel import Relationship

class PetType(Enum):
    """ Enum that describe the type of a pet """
    DOG = "dog"
    CAT = "cat"
    FISH = "fish"


class Pet(SQLModelRepository, table=True):
    """ Pet model """
    name: str
    age: int
    type: PetType
    shelter_id: int


class Shelter(SQLModelRepository, table=True):
    """ Shelter model """
    name: str
    pets: list[Pet] = Relationship(back_populates="shelter")


sqlmodel_metadata = SQLModelRepository.metadata
