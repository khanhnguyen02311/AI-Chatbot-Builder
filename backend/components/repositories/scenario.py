from sqlalchemy import select, update, delete
from . import BaseRepository
from components.data import REDIS_SESSION
from components.data.models import postgres as PostgresModels
from components.data.schemas import scenario as ScenarioSchemas


class ScenarioRepository(BaseRepository):
    def __init__(self, session):
        super().__init__(session=session, redis_session=REDIS_SESSION)

    def get(self, identifier: int):
        query = select(PostgresModels.Scenario).filter(PostgresModels.Scenario.id == identifier)
        scenario = self.session.scalar(query)
        return scenario

    def get_all(self):
        super().get_all()

    def get_all_by_account(self, identifier: int):
        query = select(PostgresModels.Scenario).filter(PostgresModels.Scenario.id_account == identifier)
        scenarios = self.session.scalars(query).all()
        return scenarios

    def create(self, new_scenario: PostgresModels.Scenario):
        self.session.add(new_scenario)
        self.session.flush()

    def update(self, identifier: int, new_data: ScenarioSchemas.ScenarioPUT):
        query = update(PostgresModels.Scenario).returning(PostgresModels.Scenario).where(PostgresModels.Scenario.id == identifier).values(**new_data.model_dump(exclude_none=True))
        new_scenario_data = self.session.scalar(query)
        self.session.flush()
        return new_scenario_data

    def delete(self, identifier: int):
        delete_query = delete(PostgresModels.Scenario).where(PostgresModels.Scenario.id == identifier)
        self.session.execute(delete_query)
        self.session.flush()
        return object
