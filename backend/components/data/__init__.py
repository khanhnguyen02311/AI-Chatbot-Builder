import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import postgres as p_models
from configurations import Postgres, SQLAlchemy, Redis

# For PostgresSQL
POSTGRES_ENGINE = create_engine(url=Postgres.URL,
                                echo=SQLAlchemy.ECHO,
                                pool_size=SQLAlchemy.POOL_SIZE,
                                max_overflow=SQLAlchemy.MAX_OVERFLOW,
                                pool_pre_ping=SQLAlchemy.POOL_PRE_PING)

POSTGRES_SESSION_FACTORY = sessionmaker(bind=POSTGRES_ENGINE,
                                        autoflush=SQLAlchemy.AUTO_FLUSH,
                                        autocommit=SQLAlchemy.AUTO_COMMIT)

p_models.Base.metadata.drop_all(POSTGRES_ENGINE)
p_models.Base.metadata.create_all(POSTGRES_ENGINE)

# For Redis
REDIS_SESSION = redis.Redis(host=Redis.HOST, port=Redis.PORT, db=Redis.DB, password=Redis.PASSWORD)
REDIS_SESSION.flushdb()
