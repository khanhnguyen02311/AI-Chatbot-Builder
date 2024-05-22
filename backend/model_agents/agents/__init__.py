from abc import ABC, abstractmethod


class Agent(ABC):
    @abstractmethod
    def load_prompt_template(self, *args, **kwargs):
        print("Load prompt template method not implemented")
        raise NotImplementedError

    @abstractmethod
    def load_tools(self, tool_list):
        print("Load tools method not implemented")
        raise NotImplementedError

    @abstractmethod
    def load_conversation(self, *args, **kwargs):
        print("Load memory method not implemented")
        raise NotImplementedError

    @abstractmethod
    def load_model(self, *args, **kwargs):
        print("Load model method not implemented")
        raise NotImplementedError

    @abstractmethod
    def generate_response(self, user_input):
        print("Generate response method not implemented")
        raise NotImplementedError
