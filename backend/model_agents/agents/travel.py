import os
from abc import ABC
from configurations.envs import App
import langchain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain_community.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory
from langchain.agents import AgentExecutor, create_react_agent
from . import ChatAgentBase
from model_agents.tools import get_tools_by_names


class ChatAgentTravel(ChatAgentBase, ABC):
    def __init__(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 0.5, max_tokens: int = 2048):
        self.prompt = None
        self.tools = []
        self.llm = None
        self.agent = None
        self.agent_chain = None
        self.memory = None

        self.load_prompt_template()
        self.load_tools(["google_search", "weather_search"])
        self.load_model(model_name, temperature, max_tokens)
        self.load_conversation()
        # self.memory = CombinedMemory(memories=[self.summary_memory, self.conversation_memory], input_key="input")

    def load_prompt_template(self):
        template = """You are Assistant, a large language model trained by OpenAI. Assistant will play the role of a travel chatbot specialized in Vietnamese tourism.
Assistant is a powerful chatbot that can help with a wide range of tasks and provide valuable, true information on a wide range of topics related to travel and tourism. Whether the Human need help with a specific question or just want to have a conversation about a particular subject, Assistant is here to assist.
As a language model, Assistant is able to generate human-like text based on the input it received, allowing it to engage in natural-sounding conversations and provide responses that are coherent and relevant to the topic at hand.
As a travel chatbot, Assistant needs to answer relevant, accurate and helpful information about Vietnamese tourism based on real data. Assistant will have access to a wide range of tools that can help with the task.
Overall, Assistant is here to help and provide valuable information to the Human, and will do its best to provide accurate and helpful responses to any questions or requests. If there is anything that Assistant is not sure about, you will let the Human know and ask for clarification or further information.

TOOLS:
------
Assistant has access to the following tools to use in the thinking process:

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
        self.tools = get_tools_by_names(tool_list)

    def load_model(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 1, max_token: int = 2048):
        self.llm = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)
        self.agent = create_react_agent(llm=self.llm, tools=self.tools, prompt=self.prompt)

    def load_conversation(self):
        # load messages from database, for later
        self.memory = ConversationBufferWindowMemory(memory_key="conversation_history", input_key="input", ai_prefix="Assistant", k=4)
        self.agent_chain = AgentExecutor.from_agent_and_tools(agent=self.agent, tools=self.tools, memory=self.memory, verbose=App.DEBUG)

    def generate_response(self, user_input: str):
        response = self.agent_chain.invoke({"input": user_input}, return_only_outputs=True)
        return response['output']

    async def generate_response_with_callback(self, user_input: str):
        with get_openai_callback() as cb:
            response = await self.agent_chain.ainvoke({"input": user_input}, return_only_outputs=True)
            print(cb)
            return response['output']
