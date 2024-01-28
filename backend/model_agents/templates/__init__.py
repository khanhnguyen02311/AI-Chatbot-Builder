from typing import List

from pydantic import BaseModel, Field


# create template based on bot
class ChatTemplate(BaseModel):
    name: str = Field(example="Testing Bot")
    description: str = Field(example="A chatbot that helps you with your finances.")
    business_fields: List[str] = Field(example=["Finance"])
    business_information: str = Field(example="We are a financial services company that provides loans.")
    response_attitude: str = Field(example="Friendly")
