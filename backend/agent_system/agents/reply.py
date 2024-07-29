from abc import ABC
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent, create_openai_tools_agent
from langchain_core.messages.base import BaseMessage
from configurations.arguments import APP_DEBUG
from configurations.envs import ChatModels
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.repositories.bot_context import BotContextRepository
from . import Agent
from agent_system.tools import get_tools_by_names, get_retriever_tools_by_bot_context


class ReplyAgent(Agent, ABC):
    def __init__(self):
        self.tools = []
        self.agent_chain = None

        template = """You are an Agent working with other members. Your job is to compose the final response to send to the Human, based on the team conversation.
Make sure the message is fully based on the previous work of other members, don't make things up. If it's a question, you need to make sure the context of the question is clear and consise.
You need to ensure all communication is detailed, clear, polite, and in the same language as the Human (mainly Vietnamese)."""

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
                ("system", "Given the conversation above, what do we reply to the Human?"),
            ]
        )
        self.load_tools(["search_google"])
        self.load_model()
        self.load_chain()

    def load_prompt_template(self):
        super().load_prompt_template()

    def load_tools(self, tool_list: list):
        self.tools += get_tools_by_names(tool_list)

    def load_conversation(self):
        super().load_conversation()

    def load_model(self, model_name: str = "gpt-4o", temperature: float = 0.5, max_token: int = 4000):
        if model_name not in ChatModels.ALLOWED_LLM_MODEL_NAMES:
            raise NotImplementedError(
                "Model not supported for now. Currently supported: " + ", ".join(ChatModels.ALLOWED_LLM_MODEL_NAMES)
            )
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        self.agent = create_openai_tools_agent(self.llm, self.tools, self.prompt)

    def load_chain(self):
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=APP_DEBUG,
            max_execution_time=10,
            max_iterations=1,
        )

    def generate_response(self, user_input: str):
        response = self.agent_chain.invoke({"input": user_input}, return_only_outputs=True)
        return response["output"]

    async def generate_response_async(self, user_input: str):
        response = await self.agent_chain.ainvoke({"input": user_input}, return_only_outputs=True)
        return response["output"]
