from abc import ABC, abstractmethod


class ChatAgentBase(ABC):
    def __init__(self, *args, **kwargs):
        pass

    @abstractmethod
    def load_prompt_template(self, template):
        print("Load prompt template method not implemented")
        raise NotImplementedError

    @abstractmethod
    def load_model(self):
        print("Load model method not implemented")
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, new_message):
        print("Generate response method not implemented")
        raise NotImplementedError
