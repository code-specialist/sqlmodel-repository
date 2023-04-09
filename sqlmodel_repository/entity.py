from sqlmodel import Field, SQLModel


class SQLModelEntity(SQLModel):
    """Base SQLModel Entity"""

    id: int = Field(index=True, default=None, primary_key=True)
