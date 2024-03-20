from fastapi import APIRouter, Depends, HTTPException, status
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models.postgres import Account
from components.data.schemas import scenario as ScenarioSchemas
from components.services.account import AccountService
from components.services.scenario import ScenarioService

router = APIRouter(prefix="/scenario")


@router.get("")
def get_all_scenarios(account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        scenario_service = ScenarioService(session=session, account=account)
        scenarios = scenario_service.get_user_scenarios()
        return ScenarioSchemas.ListScenarioGET.model_validate(scenarios)


@router.post("")
def create_scenario(data: ScenarioSchemas.ScenarioPOST, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        scenario_service = ScenarioService(session=session, account=account)
        new_scenario, err = scenario_service.create_scenario(data)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        session.commit()
        return ScenarioSchemas.ScenarioGET.model_validate(new_scenario)


@router.get("/{scenario_id}")
def get_scenario(scenario_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        scenario_service = ScenarioService(session=session, account=account)
        scenario = scenario_service.get_user_scenario(scenario_id)
        if scenario is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scenario not found")
        return ScenarioSchemas.ScenarioGET.model_validate(scenario)


@router.put("/{scenario_id}")
def update_scenario(scenario_id: int, data: ScenarioSchemas.ScenarioPUT, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        scenario_service = ScenarioService(session=session, account=account)
        updated_scenario, err = scenario_service.update_scenario(scenario_id, data)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=err)
        session.commit()
        return ScenarioSchemas.ScenarioGET.model_validate(updated_scenario)


@router.delete("/{scenario_id}")
def delete_scenario(scenario_id: int, account: Account = Depends(AccountService.validate_token)):
    with POSTGRES_SESSION_FACTORY() as session:
        scenario_service = ScenarioService(session=session, account=account)
        err = scenario_service.delete_scenario(scenario_id)
        if err is not None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=err)
        session.commit()
        return "Deleted"
