import os
from os import environ
from dotenv import load_dotenv
from .arguments import APP_STAGE

if environ.get("POSTGRES_HOST") is None:  # local environment needs to load .env file manually
    exist_loaded_env = load_dotenv(dotenv_path=f'{os.path.dirname(__file__)}/../.env.{APP_STAGE}', verbose=True)
    if not exist_loaded_env:
        raise FileNotFoundError(f"Cannot find .env.{APP_STAGE} file. If you are running in local environment, please create one using the .env.example file as reference.")


class Security:
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


class ChatModels:
    HUGGINGFACE_API_KEY = environ.get("HUGGINGFACE_API_KEY")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
    GOOGLE_API_KEY = environ.get("GOOGLE_API_KEY")
    GOOGLE_CSE_ID = environ.get("GOOGLE_CSE_ID")
    OPENWEATHERMAP_API_KEY = environ.get("OPENWEATHERMAP_API_KEY")


class Chat:
    FACEBOOK_VERIFY_TOKEN = environ.get("FACEBOOK_VERIFY_TOKEN")
    FACEBOOK_PAGE_ACCESS_TOKEN = environ.get("FACEBOOK_PAGE_ACCESS_TOKEN")
    FACEBOOK_VERSION = "v19.0"
