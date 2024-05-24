from abc import ABC
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent
from langchain_core.messages.base import BaseMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.human import HumanMessage
from configurations.arguments import APP_STAGE, APP_DEBUG
from . import Agent
from agent_system.tools import get_tools_by_names
from components.data.models import postgres as PostgresModels


class AccountAgent(Agent, ABC):
    def __init__(self, bot_data: PostgresModels.Bot, message_history: list[BaseMessage] = None):
        self.prompt = None
        self.tools = []
        self.llm = None
        self.agent = None
        self.memory = None
        self.agent_chain = None

        self.load_prompt_template(bot_data.conf_instruction)
        self.load_tools(["search_google", "search_weather"])
        if bot_data.conf_external_data is not None:
            self.load_external_data(bot_data.conf_external_data)
        self.load_model(bot_data.conf_model_name, bot_data.conf_model_temperature, 3000)
        self.load_conversation(message_history if message_history is not None else [])
        self.load_chain()

    def load_prompt_template(self, prompt):
        template = """You are Assistant, a large language model trained by OpenAI. """ + prompt + """
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
Final Answer: [your response here, in the same language as the Human]
```

Begin!

Previous conversation history:
{conversation_history}

New input: {input}
{agent_scratchpad}"""
        self.prompt = PromptTemplate(input_variables=['agent_scratchpad', 'conversation_history', 'input', 'tool_names', 'tools'], template=template)

    def load_tools(self, tool_list: list):
        self.tools += get_tools_by_names(tool_list)

    def load_external_data(self, data):
        print("Load_external_data not implemented")
        pass

    def load_conversation(self, history: list[BaseMessage]):
        # load messages from database, for later
        self.memory = ConversationBufferWindowMemory(memory_key="conversation_history", input_key="input", ai_prefix="Assistant", k=4)
        self.memory.chat_memory.messages = history

    def load_model(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 0.5, max_token: int = 3000):
        if model_name not in ["gpt-3.5-turbo-1106", "gpt-3.5-turbo"]:
            raise NotImplementedError("Model not supported for now. Currently supported: gpt-3.5-turbo-1106, gpt-3.5-turbo")
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def load_chain(self):
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=self.tools, memory=self.memory, verbose=APP_DEBUG, max_execution_time=15, max_iterations=10)

    def generate_response(self, user_input: str):
        response = self.agent_chain.invoke({"input": user_input}, return_only_outputs=True)
        return response['output']

    async def generate_response_async(self, user_input: str):
        response = await self.agent_chain.ainvoke({"input": user_input}, return_only_outputs=True)
        return response['output']
