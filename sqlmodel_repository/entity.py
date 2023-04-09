from sqlmodel import SQLModel, Field


class SQLModelEntity(SQLModel):
    """Base SQLModel Entity"""

    id: int = Field(index=True, default=None, primary_key=True)
