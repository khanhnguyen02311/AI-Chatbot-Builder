from os import environ
from .arguments import parse_args

# load command-line arguments before initializing the configuration classes
args = parse_args()


class App:
    API_PORT = int(environ.get("APP_API_PORT"))
    DEBUG = args.debug
    STAGE = args.stage


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
    ECHO = True
    AUTO_FLUSH = True  # flush after committing
    AUTO_COMMIT = False
    POOL_SIZE = 15
    MAX_OVERFLOW = 10
    POOL_PRE_PING = False


class ChatModels:
    HUGGINGFACE_API_KEY = environ.get("HUGGINGFACE_API_KEY")
    OPENAI_API_KEY = environ.get("OPENAI_API_KEY")
