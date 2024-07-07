import os
from os import environ
from dotenv import load_dotenv
from passlib.context import CryptContext
from .arguments import APP_STAGE

if environ.get("POSTGRES_HOST") is None:  # local environment needs to load .env file manually
    exist_loaded_env = load_dotenv(dotenv_path=f"{os.path.dirname(__file__)}/../.env.{APP_STAGE}", verbose=True)
    if not exist_loaded_env:
        raise FileNotFoundError(
            f"Cannot find .env.{APP_STAGE} file. If you are running in local environment, please create one using the .env.example file as reference."
        )

if not os.path.exists(f"{os.path.dirname(__file__)}/../etc/userdata"):
    os.makedirs(f"{os.path.dirname(__file__)}/../etc/userdata")


class General:
    BOT_CONTEXT_FILE_LOCATION = f"{os.path.dirname(__file__)}/../etc/userdata"
    BOT_CONTEXT_ALLOWED_MIME_TYPES = [
        "text/plain",
        "application/pdf",
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        "application/doc",
        "application/ms-doc",
        "application/msword",
    ]


class Security:
    # problems with bcrypt library in passlib
    # DEFAULT_PASSWORD_CONTEXT = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__default_rounds=11)
    DEFAULT_PASSWORD_CONTEXT = CryptContext(schemes=["sha256_crypt"], deprecated="auto", sha256_crypt__default_rounds=400000)

    JWT_SECRET_KEY = environ.get("SECURITY_JWT_SECRET_KEY")
    JWT_ALGORITHM = "HS256"
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES = int(environ.get("SECURITY_JWT_ACCESS_TOKEN_MINUTE"))
    JWT_REFRESH_TOKEN_EXPIRE_MINUTES = int(environ.get("SECURITY_JWT_REFRESH_TOKEN_MINUTE"))


class Postgres:
    HOST = environ.get("POSTGRES_HOST")
    DB = environ.get("POSTGRES_DB")
    USER = environ.get("POSTGRES_USER")
    PASSWORD = environ.get("POSTGRES_PASSWORD")
    PORT = int(environ.get("POSTGRES_PORT"))
    URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}?sslmode=disable"


class Redis:
    HOST = environ.get("REDIS_HOST")
    PORT = int(environ.get("REDIS_PORT"))
    PASSWORD = environ.get("REDIS_PASSWORD")
    DB = int(environ.get("REDIS_DB"))


class SQLAlchemy:
    # ECHO = True
    AUTO_FLUSH = True  # flush after committing
    AUTO_COMMIT = False
    POOL_SIZE = 15
    MAX_OVERFLOW = 10
    POOL_PRE_PING = False


class Qdrant:
    HOST = environ.get("QDRANT_HOST")
    PORT = int(environ.get("QDRANT_PORT"))
    COLLECTION_PREFIX = environ.get("QDRANT_COLLECTION_PREFIX")


class ChatModels:
    HUGGINGFACE_API_KEY = environ.get("HUGGINGFACE_API_KEY")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    GOOGLE_API_KEY = environ.get("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = environ.get("GOOGLE_CSE_ID")
    OPENWEATHERMAP_API_KEY = environ.get("OPENWEATHERMAP_API_KEY")
    DEFAULT_EMBEDDING_MODEL_NAME = "openai@text-embedding-3-small"
    ALLOWED_EMBEDDING_MODELS = {
        "openai@text-embedding-3-small": 1536,
        "openai@text-embedding-3-large": 3072,
        # "vinai@phobert-base": 768,
        # "vinai@phobert-base-v2": 768
    }
    ALLOWED_LLM_MODEL_NAMES = ["gpt-4-turbo", "gpt-3.5-turbo-0125", "gpt-3.5-turbo-1106", "gpt-3.5-turbo"]


class Chat:
    FACEBOOK_VERIFY_TOKEN = environ.get("FACEBOOK_VERIFY_TOKEN")
    FACEBOOK_PAGE_ACCESS_TOKEN = environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    FACEBOOK_VERSION = "v19.0"
