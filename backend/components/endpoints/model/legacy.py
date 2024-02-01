from fastapi import APIRouter
from model_agents.data.schemas.chat import ChatTemplate
from model_agents.chat.openai import ChatAgentOpenAI

router = APIRouter(prefix="/legacy")


@router.post("/test-model")
def test_model(template: ChatTemplate, question: str):
    model = ChatAgentOpenAI()
    model.load_prompt_template(template)
    response = model.generate_response(question)
    return {"response": response}
