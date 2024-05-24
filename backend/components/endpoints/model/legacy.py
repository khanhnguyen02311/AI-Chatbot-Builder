from fastapi import APIRouter
from agent_system.data.schemas.chat import ChatTemplate
from agent_system.agents.general import GeneralAgent
from agent_system.agents.travel import TravelAgent
from pydantic import BaseModel

legacy_temp_id = 0


class TravelModel(BaseModel):
    user_id: int
    question: str


router = APIRouter(prefix="/legacy")
agent_map = {}


@router.get("/new-id")
def get_new_id():
    global legacy_temp_id
    legacy_temp_id += 1
    return {"id": legacy_temp_id}


@router.post("/general-model")
def test_general_model(template: ChatTemplate, question: str):
    model = GeneralAgent()
    model.load_prompt_template(template)
    response = model.generate_response(question)
    return {"response": response}


@router.post("/travel-model")
async def test_travel_model(data: TravelModel):
    if data.user_id not in agent_map:
        agent_map[data.user_id] = TravelAgent()
    response = await agent_map[data.user_id].generate_response_with_callback(data.question)
    return {"response": response}
