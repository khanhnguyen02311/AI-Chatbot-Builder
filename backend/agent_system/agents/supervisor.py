from abc import ABC
from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_core.output_parsers.openai_functions import JsonOutputFunctionsParser
from langchain_core.messages import BaseMessage, HumanMessage
from configurations.arguments import APP_DEBUG
from . import Agent


class SupervisorAgent(Agent, ABC):
    def __init__(self, message_history: list[BaseMessage], members: list[str]):
        self.agent_chain = None
        system_prompt = (
            "You are a supervisor tasked with managing a conversation with the Human, and between the"
            " following workers:\n{members}.\nGiven the following conversation history and the current user request,"
            " respond with the worker to act next. Each worker will perform a"
            " task and respond with their results and status. When you have enough information to answer the Human,"
            " or you think you don't need any members to help you to answer that question, or the team ask for more information from the Human,"
            " respond with FINISH, another member will compose the final response."
        )
        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", system_prompt),
                MessagesPlaceholder(variable_name="messages"),
                (
                    "system",
                    "Given the conversation above, who should act next? Or should we FINISH? Select one of: {options}",
                ),
            ]
        )
        self.load_prompt_template(message_history, members)
        self.load_model()
        self.load_chain()

    def load_prompt_template(self, message_history: list[BaseMessage], members: list[str]):
        self.prompt_options = ["FINISH"] + members
        self.prompt = self.prompt.partial(
            options=str(self.prompt_options),
            members=", ".join(members),
            message_history=message_history[-5:],
        )

    def load_tools(self):
        return super().load_tools()

    def load_conversation(self, *args, **kwargs):
        return super().load_conversation()

    def load_model(self):
        self.model = ChatOpenAI(model="gpt-4o-mini")

    def load_chain(self):
        function_def = {
            "name": "route",
            "description": "Select the next role.",
            "parameters": {
                "title": "routeSchema",
                "type": "object",
                "properties": {
                    "next": {
                        "title": "Next",
                        "anyOf": [
                            {"enum": self.prompt_options},
                        ],
                    },
                },
                "required": ["next"],
            },
        }
        self.agent_chain = (
            self.prompt
            | self.model.bind_functions(functions=[function_def], function_call="route")
            | JsonOutputFunctionsParser()
        )

    def generate_response(self, user_input: str):
        return self.agent_chain.invoke({"messages": [HumanMessage(content=user_input)]})
