from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """
    DEBUG: bool = False

    POSTGRES_USER: str
    POSTGRES_PASSWORD: str
    POSTGRES_DB: str
    POSTGRES_HOST: str
    POSTGRES_PORT: int
    
    INTERNAL_TOKEN: str
    OPENAI_API_KEY: str

    @property
    def database_url(self) -> str:
        """
        Constructs the database URL for PostgreSQL.
        """
        return f"postgresql+asyncpg://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"

    class Config:
        env_file = "../.env"


settings = Settings.model_validate({})