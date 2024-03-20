from fastapi import APIRouter
from model_agents.data.schemas.chat import ChatTemplate
from model_agents.agents.general import ChatAgentGeneral
from model_agents.agents.travel import ChatAgentTravel
from pydantic import BaseModel


class TravelModel(BaseModel):
    user_id: int
    question: str


router = APIRouter(prefix="/legacy")
agent_map = {}


@router.post("/general-model")
def test_general_model(template: ChatTemplate, question: str):
    model = ChatAgentGeneral()
    model.load_prompt_template(template)
    response = model.generate_response(question)
    return {"response": response}


@router.post("/travel-model")
async def test_travel_model(data: TravelModel):
    if data.user_id not in agent_map:
        agent_map[data.user_id] = ChatAgentTravel()
    response = await agent_map[data.user_id].generate_response_with_callback(data.question)
    return {"response": response}
