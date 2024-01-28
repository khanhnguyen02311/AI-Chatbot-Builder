import os
import langchain
from langchain.chat_models import ChatOpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import ConversationChain
from langchain.callbacks import get_openai_callback
from langchain.memory import ConversationBufferWindowMemory, CombinedMemory, ConversationSummaryMemory
from models.templates import ChatTemplate


class ChatModelOpenAI:
    def __init__(self, message_history, template_data: ChatTemplate, model_name: str = "gpt-3.5-turbo-1106"):
        if model_name not in ["gpt-3.5-turbo-1106", "gpt-3.5-turbo"]:
            raise ValueError("Model not supported for now.")

        self.summary_memory = None
        self.conversation_memory = None
        self.memory = None
        self.template = None
        self.model = None

        self.name = template_data.name
        self.model_name = model_name
        self.template_data = template_data

        self.load_prompt_template()

    def load_prompt_template(self):
        self.summary_memory = ConversationSummaryMemory(memory_key="summary_history", input_key="input", human_prefix="Customer")
        self.conversation_memory = ConversationBufferWindowMemory(memory_key="conversation_history", input_key="input", human_prefix="Customer", k=5)
        self.memory = CombinedMemory(memories=[self.summary_memory, self.conversation_memory], input_key="input")

        template = """Acts as a customer service representative for a business in """ + ', '.join(self.template_data.business_fields) + """ field(s).
- Your descriptions: """ + self.template_data.description + """
- Business information:\n""" + self.template_data.business_information + """
- Your communication requirements:\n""" + self.template_data.response_attitude + """
- Chat summary:\n{summary_history}
- Chat history:\n{conversation_history}
Customer: {input}
AI (reply here): """
        self.template = PromptTemplate(input_variables=["summary_memory", "conversation_memory", "input"], template=template)

    def load_model(self):
        self.model = ChatOpenAI(model_name=self.template_data.model_name, template=self.template, memory=self.memory)
