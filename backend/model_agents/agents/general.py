import os
from abc import ABC
import langchain
from langchain_openai import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain_community.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory, CombinedMemory, ConversationSummaryMemory
from . import Agent
from model_agents.data.schemas import chat as ChatSchemas


class GeneralAgent(Agent, ABC):
    def __init__(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 1, max_tokens: int = 2048):
        if model_name not in ["gpt-3.5-turbo-1106", "gpt-3.5-turbo"]:
            raise NotImplementedError("Model not supported for now.")

        self.model_name = model_name
        self.model = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_tokens)
        self.prompt = None

        self.summary_memory = ConversationSummaryMemory(llm=self.model, memory_key="summary_history", input_key="input", human_prefix="Customer")
        self.conversation_memory = ConversationBufferWindowMemory(memory_key="conversation_history", input_key="input", human_prefix="Customer", k=3)
        self.memory = CombinedMemory(memories=[self.summary_memory, self.conversation_memory], input_key="input")

    def load_prompt_template(self, template_data: ChatSchemas.ChatTemplate):
        template = """You are a chatbot talking with a customer. Your role is being a customer service representative for a business in """ + ', '.join(
            template_data.business_fields) + """ field(s). These are further information about you and the business:
- Your descriptions: """ + template_data.description + """
- Business information:\n""" + template_data.business_information + """
- Your communication requirements:\n""" + template_data.response_attitude + """

These are the information about the current conversation and the place to write your response.
- Chat summary:
{summary_history}

- Chat history:
{conversation_history}
Customer: {input}
AI: """
        self.prompt = PromptTemplate(input_variables=["summary_memory", "conversation_memory", "input"], template=template)

    def load_model(self, model_name: str = "gpt-3.5-turbo-1106", temperature: float = 1, max_token: int = 2048):
        self.model_name = model_name
        self.model = ChatOpenAI(model_name=model_name, temperature=temperature, max_tokens=max_token)

    def load_conversation(self):
        conversation = LLMChain(llm=self.model, memory=self.memory, prompt=self.prompt, verbose=False)
        return conversation

    def generate_response(self, new_message: str):
        conversation = self.load_conversation()
        with get_openai_callback() as cb:
            response = conversation.predict(input=new_message)
            print(cb)
        return response
