from pydantic import BaseSettings, Field


class SQLModelRepositoryConfig(BaseSettings):
    """The configuration for the sqlmodel repository"""

    DATABASE_URL: str = Field(env="DATABASE_URL", default="postgresql://postgres:postgres@localhost:5432/test", description="The database url that is used to connect to the database")

    class Config:
        """Pydantic configuration"""

        env_file = ".env"
        env_file_encoding = "utf-8"


sqlmodel_repository_config: SQLModelRepositoryConfig = SQLModelRepositoryConfig()
