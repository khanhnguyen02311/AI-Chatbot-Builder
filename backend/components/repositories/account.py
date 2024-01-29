from sqlalchemy import select, update, delete
from . import BaseRepository
from configurations import Security
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import postgres as PostgresSchemas


class AccountRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, redis_session=REDIS_SESSION)

    def get_no_cache(self, identifier: int) -> PostgresModels.Account:
        query = select(PostgresModels.Account).filter(PostgresModels.Account.id == identifier)
        account = self.session.scalar(query)
        return account

    def get(self, identifier: int) -> PostgresModels.Account:
        cached_data = self.redis_session.get(f"AccountFULL:{identifier}")
        if cached_data:
            return PostgresModels.Account(**PostgresSchemas.AccountFULL.model_load_json(cached_data))
        else:
            account = self.get_no_cache(identifier)
            if account:
                self.redis_session.setex(f"AccountFULL:{identifier}", Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                                         PostgresSchemas.AccountFULL.model_validate(account).model_dump_json())
                return account

    def get_all(self):
        super().get_all()

    def create(self, new_account: PostgresModels.Account):
        self.session.add(new_account)
        self.session.flush()
        self.redis_session.setex(f"AccountFULL:{new_account.id}", Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                                 PostgresSchemas.AccountFULL.model_validate(new_account).model_dump_json())

    def update(self, identifier: int, new_data: PostgresSchemas.AccountPUT):
        query = update(PostgresModels.Account).returning(PostgresModels.Account).where(PostgresModels.Account.id == identifier).values(**new_data.model_dump(exclude_none=True))
        new_account_data = self.session.scalar(query)
        self.session.flush()
        self.redis_session.setex(f"AccountFULL:{identifier}", Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
                                 PostgresSchemas.AccountFULL.model_validate(new_account_data).model_dump_json())
        return new_account_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.Account).where(PostgresModels.Account.id == identifier)
        self.session.execute(delete_query)
        self.session.flush()
        return object
