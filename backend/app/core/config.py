import os
from dotenv import load_dotenv

load_dotenv()

class Settings:
    DB_HOST: str = os.getenv("host")
    DB_PORT: int = int(os.getenv("port", 3306))
    DB_USER: str = os.getenv("user")
    DB_PASSWORD: str = os.getenv("password")
    DB_NAME: str = os.getenv("database")

    # Add any other environment variables needed, e.g., API keys for external services
    # OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY")

settings = Settings()

# Database configuration dictionary for singlestoredb
DATABASE_CONFIG = {
    "host": settings.DB_HOST,
    "port": settings.DB_PORT,
    "user": settings.DB_USER,
    "password": settings.DB_PASSWORD,
    "database": settings.DB_NAME
} 