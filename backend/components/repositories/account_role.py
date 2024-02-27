from sqlalchemy import select
from . import BaseRepository
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import account_role as AccountRoleSchemas


class AccountRoleRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, redis_session=REDIS_SESSION)

    @classmethod
    def default_roles(cls):
        return ["Admin", "User"]

    def get_by_role(self, role: str):
        cached_data = self.redis_session.get(f"AccountRole:{role}")
        if cached_data:
            return PostgresModels.AccountRole(**AccountRoleSchemas.AccountRoleFULL.model_validate_json(cached_data).model_dump())
        else:
            query = select(PostgresModels.AccountRole).filter(PostgresModels.AccountRole.role == role)
            account_role = self.session.scalar(query)
            if account_role is not None:
                self.redis_session.set(f"AccountRole:{role}",
                                       AccountRoleSchemas.AccountRoleFULL.model_validate(account_role).model_dump_json())
            return account_role

    def get(self, identifier: int):
        query = select(PostgresModels.AccountRole).filter(PostgresModels.AccountRole.id == identifier)
        account_role = self.session.scalar(query)
        if account_role is not None:
            self.redis_session.set(f"AccountRole:{account_role.role}",
                                   AccountRoleSchemas.AccountRoleFULL.model_validate(account_role).model_dump_json())
            return account_role

    def get_all(self):
        query = select(PostgresModels.AccountRole)
        account_roles = self.session.scalars(query).all()
        for account_roles_obj in account_roles:
            self.redis_session.set(f"AccountRole:{account_roles_obj.role}",
                                   AccountRoleSchemas.AccountRoleFULL.model_validate(account_roles_obj).model_dump_json())
        return account_roles

    def create_all(self):
        for role in self.default_roles():
            account_role = PostgresModels.AccountRole(role=role)
            self.session.add(account_role)
            self.session.flush()
            self.redis_session.set(f"AccountRole:{account_role.role}",
                                   AccountRoleSchemas.AccountRoleFULL.model_validate(account_role).model_dump_json())

    def create(self):
        super().create()

    def update(self):
        super().update()

    def delete(self):
        super().delete()

    # def create(self, new_account_role: PostgresModels.AccountRole):
    #     self.session.add(new_account_role)
    #     self.session.flush()
    #     self.redis_session.set(f"AccountRole:{new_account_role.role}",
    #                        AccountRoleSchemas.AccountRoleFULL.model_validate(new_account_role).model_dump_json())
    #
    # def update(self, identifier: int, new_data: AccountRoleSchemas.AccountRolePUT):
    #     query = select(PostgresModels.AccountRole).where(PostgresModels.AccountRole.id == identifier)
    #     account_role = self.session.scalar(query)
    #     if account_role is None:
    #         return None
    #     self.redis_session.delete(f"AccountRole:{account_role.role}")
    #     account_role.role = new_data.role
    #     self.session.flush()
    #     self.redis_session.set(f"AccountRole:{account_role.role}",
    #                           AccountRoleSchemas.AccountRoleFULL.model_validate(account_role).model_dump_json())
    #     return account_role
    #
    # def delete(self, identifier: int):
    #     query = delete(PostgresModels.AccountRole).where(PostgresModels.AccountRole.id == identifier)
    #     self.session.execute(query)
    #     self.session.flush()
    #     return object
