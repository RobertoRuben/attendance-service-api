from pydantic_settings import BaseSettings
from urllib.parse import quote_plus


class Settings(BaseSettings):
    """
    Application configuration settings loaded from environment variables.

    This class manages all configuration parameters required for database connectivity
    and other application settings. Values can be loaded from environment variables
    or from a .env file.

    Attributes:
        DB_ECHO_LOG (bool): Flag to enable/disable SQL query logging. Defaults to True.
        DB_HOST (str): Database server hostname or IP address.
        DB_PORT (str): Database server port.
        DB_NAME (str): Database name.
        DB_USER (str): Database username.
        DB_PASSWORD (str): Database password.
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

    @property
    def database_url(self) -> str:
        """
        Constructs a properly formatted PostgreSQL connection string.

        Generates a connection URL for asyncpg with properly URL-encoded username
        and password to handle special characters.

        Returns:
            str: Formatted PostgreSQL connection string for asyncpg.
        """
        user = quote_plus(self.DB_USER)
        password = quote_plus(self.DB_PASSWORD)
        return f"postgresql+asyncpg://{user}:{password}@{self.DB_HOST}:{self.DB_PORT}/{self.DB_NAME}"

    class Config:
        """
        Configuration class for pydantic settings behavior.

        Specifies the location of the environment file to load variables from.
        """

        env_file = ".env"


# Create a singleton instance of the settings
settings = Settings()