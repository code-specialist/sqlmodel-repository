from sqlmodel import SQLModel, Field


class SQLModelEntity(SQLModel):
    """ Base SQLModel Entity """

    id: int = Field(index=True, primary_key=True)
