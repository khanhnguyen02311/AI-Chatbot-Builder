import redis
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from .models import postgres as PostgresModels
from configurations.envs import Postgres, SQLAlchemy, Redis


def setup_default_data(postgres_session_factory: sessionmaker):
    with postgres_session_factory.begin() as session:
        check_existed = session.get(PostgresModels.AccountRole, 1)
        if check_existed is not None:
            return
        for role in ["Admin", "User"]:
            session.add(PostgresModels.AccountRole(role=role))
            # some e-commerce type of products
        for business_field in ["Tech", "Food & Beverage", "Fashion", "Health & Beauty", "Home & Living", "Books", "Sports & Outdoor", "Toys & Games", "Automotive",
                               "Pet Supplies", "Others"]:
            session.add(PostgresModels.BusinessField(field=business_field))
        session.flush()
        default_admin = PostgresModels.Account(username="admin123", password="admin123", email="admin123@email.com", name="Default Admin", id_account_role=1)
        session.add(default_admin)
        session.commit()


# For PostgresSQL
POSTGRES_ENGINE = create_engine(url=Postgres.URL,
                                echo=SQLAlchemy.ECHO,
                                pool_size=SQLAlchemy.POOL_SIZE,
                                max_overflow=SQLAlchemy.MAX_OVERFLOW,
                                pool_pre_ping=SQLAlchemy.POOL_PRE_PING)

POSTGRES_SESSION_FACTORY = sessionmaker(bind=POSTGRES_ENGINE,
                                        autoflush=SQLAlchemy.AUTO_FLUSH,
                                        autocommit=SQLAlchemy.AUTO_COMMIT)

# PostgresModels.Base.metadata.drop_all(POSTGRES_ENGINE)
PostgresModels.Base.metadata.create_all(POSTGRES_ENGINE)

setup_default_data(POSTGRES_SESSION_FACTORY)

# For Redis
REDIS_SESSION = redis.Redis(host=Redis.HOST, port=Redis.PORT, db=Redis.DB, password=Redis.PASSWORD)
REDIS_SESSION.flushdb()
