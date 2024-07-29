from datetime import datetime
from . import BaseORMModel, BaseListModel
from pydantic import Field, model_validator


class BotTeamFULL(BaseORMModel):
    id: int
    name: str
    description: str
    using_supervisor: bool
    using_general_bot: bool
    team_members: list[int]
    time_created: datetime
    id_account: int


class ListBotTeamFULL(BaseListModel):
    root: list[BotTeamFULL]


class BotTeamGET(BaseORMModel):
    id: int
    name: str
    description: str
    using_supervisor: bool
    using_general_bot: bool
    team_members: list[int]
    time_created: datetime


class ListBotTeamGET(BaseListModel):
    root: list[BotTeamGET]


class BotTeamPOST(BaseORMModel):
    name: str = Field(max_length=64)
    description: str = Field(min_length=16)
    using_supervisor: bool
    using_general_bot: bool
    team_members: list[int]

    @model_validator(mode="after")
    def valid_team(self):
        if self.team_members == []:
            raise ValueError("At least one team member must be provided.")
        if self.using_general_bot and not self.using_supervisor:
            raise ValueError("General travel bot is only available when use with supervisor.")
        if not self.using_supervisor and len(self.team_members) > 1:
            raise ValueError("Only single bot is allowed when not using supervisor.")
        return self


class BotTeamPUT(BotTeamPOST):
    # name: str | None = Field(max_length=64, default=None)
    # description: str | None = Field(min_length=16, default=None)
    # is_public: bool | None = None
    # conf_model_temperature: float | None = Field(ge=0.0, le=1.0, default=None)
    # conf_model_name: str | None = Field(max_length=64, default=None)
    # conf_instruction: str | None = None
    pass
