# SQLModel Repository - Python Repository Pattern Implementation for SQLModel

[![CodeQL](https://github.com/code-specialist/python-repository/actions/workflows/github-code-scanning/codeql/badge.svg)](https://github.com/code-specialist/python-repository/actions/workflows/github-code-scanning/codeql) [![Tests](https://github.com/code-specialist/python-repository/actions/workflows/test.yaml/badge.svg)](https://github.com/code-specialist/python-repository/actions/workflows/test.yaml)

SQLModel Repository implements the repository pattern and provides simple, robust and reliable CRUD operations for [SQLModels](https://sqlmodel.tiangolo.com/). The repository pattern is a great way to encapsulate the logic of your application and to separate the business logic from the data access layer.

Any contributions are welcome. But we do not accept any pull requests that do not come with tests.

## Installation

```bash
pip install sqlmodel-repository
```

## Usage

### 1. Create a Repository

To create a repository you need to inherit from the `Repository` class and pass the entity type as a generic type argument.

```python
from typing import TypeVar
from sqlalchemy.orm import Session
from sqlmodel_repository import SQLModelEntity, Repository

ExampleEntity = TypeVar("ExampleEntity", bound=SQLModelEntity)


class AbstractRepository(Repository[ExampleEntity]):
    """Example base class for all repositories"""

    def get_session(self) -> Session:
        """Provides a session to work with"""
        # TODO: Implement a method to provide a session here
```

In this example we use a `TypeVar` to pass the generic type downwards. You have to implement the `get_session` method to provide a session to the repository.

### 2. Create Entities and Relationships

```python
from enum import Enum
from sqlmodel import Relationship, Field
from sqlmodel_repository import SQLModelEntity


class PetType(Enum):
    """Enum that describes the type of pet"""

    DOG = "dog"
    CAT = "cat"
    FISH = "fish"


class Pet(SQLModelEntity, table=True):
    """Pet model"""

    id: int = Field(index=True, default=None, primary_key=True)

    name: str
    age: int
    type: PetType
    shelter_id: int = Field(foreign_key="shelter.id")
    shelter: "Shelter" = Relationship(back_populates="pets")

class Shelter(SQLModelEntity, table=True):
    """Shelter model"""

    id: int = Field(index=True, default=None, primary_key=True)

    name: str
    pets: list[Pet] = Relationship(back_populates="shelter", sa_relationship_kwargs={"cascade": "all, delete-orphan"})
```

### 3. Inherit from the Repository

Now you can inherit from your `AbstractRepository` and tell it to manage the a specific entity. e.g. `Pet` and `Shelter`:

```python
class PetRepository(AbstractRepository[Pet]):
    """Repository to manage pets"""

class ShelterRepository(AbstractRepository[Shelter]):
    """Repository to manage shelters"""
```

Done 🚀 You can now use the repository to perform the operations on your entities. e.g.:

```python
from sqlmodel import col

# Create a new shelter
shelter = ShelterRepository().create(Shelter(name="Shelter 1"))

# Create some pets
fido = PetRepository().create(Pet(name="Fido", age=3, type=PetType.DOG, shelter_id=1))
fifi = PetRepository().create(Pet(name="Fifi", age=2, type=PetType.CAT, shelter_id=1))

# Find all pets that belong to the shelter
PetRepository().find(shelter=shelter)
```

No more session passing, no more boilerplate code. Just use the repository to perform the operations on your entities 🎉

## Methods

### Repository

Each `Repository` comes with a set of **typed methods** to perform common CRUD operations on your entities:

- `create`: Create a new record of an entity
- `create_batch`: Create a batch of records of an entity

______________________________________________________________________

- `find`: Find all records of an entity that match the given filters

______________________________________________________________________

- `get_by_id`: Get a single record by its ID
- `get_batch`: Get all records of an entity that match the given filters
- `get_batch_by_ids`: Get a batch of records by their IDs
- `get_all`: Get all records of an entity

______________________________________________________________________

- `update`: Update an entity instance
- `update_by_id`: Update an entity by its ID
- `update_batch`: Update a batch of entity instances with the same values
- `update_batch_by_ids`: Update a batch of entities by their IDs

______________________________________________________________________

- `delete`: Delete an entity instance
- `delete_by_id`: Delete an entity by its ID
- `delete_batch`: Delete a batch of entity instances
- `delete_batch_by_ids`: Delete a batch of entities by their IDs

### BaseRepository

If you require more flexibility, you may also use the `BaseRepository` which provides more granular operations. The `BaseRepository` provides the following methods:

- `_create`: Create a new record of an entity
- `_create_batch`: Create a batch of records of an entity
- `_update`: Update an entity instance
- `_update_batch`: Update a batch of entity instances with the same values
- `_get`: Get a single record by its ID
- `_get_batch`: Get all records of an entity that match the given filters
- `_delete`: Delete an entity instance
- `_delete_batch`: Delete a batch of entity instances

## Examples

For a more detailed example, check out our [tests/integration/scenarios](tests/integration/scenarios) directory. We do not currently offer a full example application.
