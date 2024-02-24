from sqlalchemy import select
from . import BaseRepository
from components.data.models import postgres as PostgresModels


class BusinessFieldRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, redis_session=None)

    def get(self):
        super().get()

    def get_all(self):
        query = select(PostgresModels.BusinessField)
        business_fields = self.session.scalars(query).all()
        return business_fields

    def create(self):
        super().create()

    def update(self):
        super().update()

    def delete(self):
        super().delete()
