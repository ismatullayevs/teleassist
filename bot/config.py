from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """
    Configuration settings for the application.
    """

    BOT_TOKEN: str
    INTERNAL_TOKEN: str

    MONGO_HOST: str
    MONGO_PORT: int
    MONGO_ADMIN: str
    MONGO_PASSWORD: str

    @property
    def mongo_url(self) -> str:
        """
        Constructs the MongoDB connection URL based on the provided settings.
        """
        return f"mongodb://{self.MONGO_ADMIN}:{self.MONGO_PASSWORD}@{self.MONGO_HOST}:{self.MONGO_PORT}"


settings = Settings.model_validate({})
