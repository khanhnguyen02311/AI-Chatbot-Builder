from abc import ABC
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent, create_openai_tools_agent
from langchain_core.messages import BaseMessage
from langchain_core.prompts.chat import MessagesPlaceholder
from configurations.arguments import APP_DEBUG
from configurations.envs import ChatModels
from components.data import POSTGRES_SESSION_FACTORY
from components.data.models import postgres as PostgresModels
from components.repositories.bot_context import BotContextRepository
from . import Agent
from agent_system.tools import get_tools_by_names, get_retriever_tools_by_bot_context


class CollaborativeAgent(Agent, ABC):
    def __init__(
        self,
        bot_data: PostgresModels.Bot,
        tool_names: list[str],
        agent_names: list[str],
        message_history: list[BaseMessage] = [],
    ):
        self.name = bot_data.name
        self.prompt = None
        self.tools = []
        self.agent_names = agent_names
        self.llm = None
        self.agent = None
        self.agent_chain = None
        self.message_history = message_history
        self.load_tools(tool_names)

        with POSTGRES_SESSION_FACTORY() as session:
            bot_context_repository = BotContextRepository(session=session)
            bot_contexts = bot_context_repository.get_all_by_bot(bot_data.id)
            retriever_tools = get_retriever_tools_by_bot_context(bot_contexts)
            self.tools += retriever_tools

        self.load_prompt_template(tool_names, bot_data.conf_instruction)
        self.load_model(bot_data.conf_model_name, bot_data.conf_model_temperature, 4096)
        self.load_chain()

    def load_prompt_template(self, tool_names, instruction):
        string_tool_names = (
            "" if len(tool_names) == 0 else "You have access to the following tools: " + ", ".join(tool_names)
        )
        string_message_history = "\n".join(
            [f"{message.type.upper()}: {message.content}" for message in self.message_history[-5:]]
        )
        template = """You are a helpful AI assistant, collaborating with other assistants.
Use the provided tools to progress towards answering the question. 
If you are unable to fully answer, that's OK, response with 'GO TO: <assistant-name>', another assistant with different tools will help where you left off. The assistant name MUST be a valid assistant in the team.
Example 1: 
'GO TO: research_agent' (the progress will be passed to research_agent)
Example 2:
'GO TO: customer_agent' (the progress will be passed to customer_agent)
Your name in the team is {agent_name}. Your team consists of these assistants: {agent_list}.
Your responsibility: {instruction}
{tool_names}
The conversation history of your team with the human:
{message_history}

Your team can collab as long as you want, but if you or any of the other assistants have the final answer to the Human, you MUST prefix your response with 'FINAL ANSWER' so the team knows to stop. 
Example 1: 
'FINAL ANSWER: Hello! How can I help you?' (it will return 'Hello! How can I help you?' to the Human)
Example 2:
'FINAL ANSWER: Bạn có thể giải thích cụ thể hơn không' (it will return 'Bạn có thể giải thích cụ thể hơn không' to the Human)

Begin!
"""
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", template),
                MessagesPlaceholder(variable_name="messages"),
                MessagesPlaceholder(variable_name="agent_scratchpad"),
            ]
        )
        self.prompt = self.prompt.partial(
            tool_names=string_tool_names,
            instruction=instruction,
            message_history=string_message_history,
            agent_name=self.name,
            agent_list=", ".join(self.agent_names),
        )

    def load_conversation(self, *args, **kwargs):
        return super().load_conversation(*args, **kwargs)

    def load_tools(self, tool_list):
        self.tools += get_tools_by_names(tool_list)

    def load_model(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 0.5, max_token: int = 3000):
        if model_name not in ChatModels.ALLOWED_LLM_MODEL_NAMES:
            raise NotImplementedError(
                "Model not supported for now. Currently supported: " + ", ".join(ChatModels.ALLOWED_LLM_MODEL_NAMES)
            )
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        if self.tools != []:
            self.agent = create_openai_tools_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def load_chain(self):
        self.agent_chain = AgentExecutor.from_agent_and_tools(
            agent=self.agent,
            tools=self.tools,
            verbose=APP_DEBUG,
            max_execution_time=15,
            max_iterations=7,
        )

    # don't need to use this because we don't have input placeholder
    def generate_response(self, user_input: str):
        response = self.agent_chain.invoke({"input": user_input}, return_only_outputs=True)
        return response["output"]
