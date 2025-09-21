from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.
    """

    API_BASE_URL: str
    DB_ECHO_LOG: bool = True
    DB_HOST: str
    DB_PORT: str
    DB_NAME: str
    DB_USER: str
    DB_PASSWORD: str

    ARGON2_TIME_COST: int = 3
    ARGON2_MEMORY_COST: int = 65536
    ARGON2_PARALLELISM: int = 4
    ARGON2_HASH_LEN: int = 32
    ARGON2_SALT_LEN: int = 16

    STORAGE_TYPE: str
    LOCAL_STORAGE_PATH: str  
    STORAGE_CREATE_DIRS: bool
    STORAGE_MAX_FILE_SIZE_MB: int

    @property
    def database_url(self) -> str:
        """
        Constructs a properly formatted PostgreSQL connection string.
        """
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql+asyncpg://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        """
        Configuration class for pydantic settings behavior.
        """

        env_file = ".env"


# Create a singleton instance of the settings
settings = Settings()
