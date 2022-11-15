from sqlmodel import SQLModel, Field


class SQLModelRepository(SQLModel):
    """ Repository pattern implementation for SQLModel """

    id: int = Field(index=True, primary_key=True)
