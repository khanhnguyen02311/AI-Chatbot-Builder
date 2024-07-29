from abc import ABC
import re
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate, ChatPromptTemplate, MessagesPlaceholder
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent as lc_create_react_agent, create_openai_tools_agent
from langgraph.prebuilt import create_react_agent as lg_create_react_agent
from langchain_core.messages.base import BaseMessage
from configurations.arguments import APP_DEBUG
from configurations.envs import ChatModels
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.repositories.bot_context import BotContextRepository
from . import Agent
from agent_system.tools import get_tools_by_names, get_retriever_tools_by_bot_context


def process_name(name_field: str) -> str:
    # Step 1: Strip any whitespace characters from the beginning and end of the string
    name_field = name_field.strip()

    # Step 2: Replace white spaces within the string with underscores
    name_field = re.sub(r"\s+", "_", name_field)

    # Step 3: Remove any characters that do not match the [a-zA-Z0-9_-] pattern
    name_field = re.sub(r"[^a-zA-Z0-9_-]", "", name_field)

    # Step 4: Truncate to 63 characters
    name_field = name_field[:63]

    return name_field

    # # Step 5: Validate against the regex pattern
    # if not re.match(r"^[a-zA-Z0-9_-]{1,63}$", name_field):
    #     raise ValueError("Invalid characters in name field")


class AccountAgent(Agent, ABC):
    def __init__(self, bot_data: PostgresModels.Bot, message_history: list[BaseMessage] = None):
        self.name = bot_data.name
        self.prompt = None
        self.chat_prompt = None
        self.tools = []
        self.llm = None
        self.agent = None
        self.memory = None
        self.agent_chain = None

        self.load_tools(["search_google", "search_weather", "scrape_website"])

        with POSTGRES_SESSION_FACTORY() as session:
            bot_context_repository = BotContextRepository(session=session)
            bot_contexts = bot_context_repository.get_all_by_bot(bot_data.id)
            retriever_tools = get_retriever_tools_by_bot_context(bot_contexts)
            self.tools += retriever_tools

        self.load_prompt_template(bot_data.conf_instruction)
        self.load_model(bot_data.conf_model_name, bot_data.conf_model_temperature, 4096)
        self.load_conversation(message_history if message_history is not None else [])
        self.load_chain()

    def load_prompt_template(self, prompt: str):
        template = (
            """You are a helpful Assistant. You will focus in this responsibility:\n"""
            + prompt
            + """
TOOLS:
------
Assistant has access to these following tools to use in the thinking process:

{tools}

If you need to use a tool, please use the following format:

```
Thought: Do I need to use a tool? Yes
Action: the action to take, should be one of [{tool_names}]
Action Input: the input to the action
Observation: the result of the action
```

When you have a response to say to the Human, or if you do not need to use a tool anymore, you MUST use the format:

```
Thought: Do I need to use a tool? No
Final Answer: [your response here, in the same language as the Human (for example Vietnamese if the Human speaks Vietnamese, or English if the Human speaks English)]
```

Begin!

Previous conversation history:
{conversation_history}

New input: 
{input}
{agent_scratchpad}"""
        )
        self.prompt = PromptTemplate(
            input_variables=["agent_scratchpad", "conversation_history", "input", "tool_names", "tools"], template=template
        )

    def load_tools(self, tool_list: list):
        self.tools += get_tools_by_names(tool_list)

    def load_conversation(self, history: list[BaseMessage]):
        # load messages from database, for later
        self.memory = ConversationBufferWindowMemory(
            memory_key="conversation_history", input_key="input", ai_prefix="Assistant", k=5
        )
        self.memory.chat_memory.messages = history

    def load_model(self, model_name: str = "gpt-3.5-turbo-0125", temperature: float = 0.5, max_token: int = 3000):
        if model_name not in ChatModels.ALLOWED_LLM_MODEL_NAMES:
            raise NotImplementedError(
                "Model not supported for now. Currently supported: " + ", ".join(ChatModels.ALLOWED_LLM_MODEL_NAMES)
            )
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        self.agent = lc_create_react_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def load_chain(self):
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            memory=self.memory,
            verbose=APP_DEBUG,
            max_execution_time=15,
            max_iterations=7,
        )

    def generate_response(self, user_input: str):
        response = self.agent_chain.invoke({"input": user_input}, return_only_outputs=True)
        return response["output"]

    async def generate_response_async(self, user_input: str):
        response = await self.agent_chain.ainvoke({"input": user_input}, return_only_outputs=True)
        return response["output"]


# -----
class AccountTeamAgent:
    def __init__(self, bot_data: PostgresModels.Bot, message_history: list[BaseMessage] = None):
        self.name = process_name(bot_data.name)
        self.prompt = None
        self.tools = []
        self.llm = None
        self.agent = None
        self.agent_chain = None

        self.load_tools(["search_google", "search_weather", "scrape_website"])

        with POSTGRES_SESSION_FACTORY() as session:
            bot_context_repository = BotContextRepository(session=session)
            bot_contexts = bot_context_repository.get_all_by_bot(bot_data.id)
            retriever_tools = get_retriever_tools_by_bot_context(bot_contexts)
            self.tools += retriever_tools

        self.load_prompt_template(bot_data.conf_instruction)
        self.load_model(bot_data.conf_model_name, bot_data.conf_model_temperature, 4096)
        self.load_chain()

    def load_tools(self, tool_list: list):
        self.tools += get_tools_by_names(tool_list)

    def load_prompt_template(self, prompt: str):
        template = (
            """You are an Assistant working in a team. You will focus in this responsibility:\n"""
            + prompt
            + """
Begin!
"""
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        # self.prompt = PromptTemplate(
        #     input_variables=["agent_scratchpad", "tool_names", "tools", "messages"], template=template
        # )

    def load_model(self, model_name: str = "gpt-3.5-turbo-0125", temperature: float = 0.5, max_token: int = 3000):
        if model_name not in ChatModels.ALLOWED_LLM_MODEL_NAMES:
            raise NotImplementedError(
                "Model not supported for now. Currently supported: " + ", ".join(ChatModels.ALLOWED_LLM_MODEL_NAMES)
            )
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        self.agent = create_openai_tools_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def load_chain(self):
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            # verbose=APP_DEBUG,
            # max_execution_time=15,
            # max_iterations=7,
        )
