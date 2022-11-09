from sqlmodel import SQLModel, Field


class SQLModelRepository(SQLModel, table=True):
    """ Repository pattern implementation for SQLModel """

    id: int = Field(index=True, primary_key=True)
