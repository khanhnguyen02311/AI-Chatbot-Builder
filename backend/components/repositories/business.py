from sqlalchemy import select, update, delete
from . import BaseRepository
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import business as BusinessSchemas


class BusinessRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, redis_session=REDIS_SESSION)

    def get(self, identifier: int):
        query = select(PostgresModels.Business).filter(
            PostgresModels.Business.id == identifier
        )  # .join(PostgresModels.Account)
        business = self.session.scalar(query)
        return business

    def get_all(self):
        super().get_all()

    def get_all_by_account(self, identifier: int):
        query = select(PostgresModels.Business).filter(PostgresModels.Business.id_account == identifier)
        businesses = self.session.scalars(query).all()
        return businesses

    def create(self, new_business: PostgresModels.Business):
        self.session.add(new_business)
        self.session.flush()

    def update(self, identifier: int, new_data: BusinessSchemas.BusinessPUT):
        query = (
            update(PostgresModels.Business)
            .returning(PostgresModels.Business)
            .where(PostgresModels.Business.id == identifier)
            .values(**new_data.model_dump(exclude_none=True))
        )
        new_business_data = self.session.scalar(query)
        self.session.flush()
        # self.redis_session.setex(f"BusinessFULL:{identifier}", Security.JWT_REFRESH_TOKEN_EXPIRE_MINUTES * 60,
        #                          BusinessSchemas.BusinessFULL.model_validate(new_business_data).model_dump_json())
        return new_business_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.Business).where(PostgresModels.Business.id == identifier)
        self.session.execute(delete_query)
        self.session.flush()
        return object
