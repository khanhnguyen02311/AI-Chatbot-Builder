from abc import ABC, abstractmethod
from typing import Any
from sqlalchemy.orm import Session
import redis


class BaseRepository(ABC):
    def __init__(self, *args, **kwargs):
        self.session: Session = kwargs.get("session")
        self.redis_session: redis.Redis = kwargs.get("redis_session")

    @abstractmethod
    def get(self, *args, **kwargs):
        print("Repository get method called but not implemented")
        pass

    @abstractmethod
    def get_all(self, *args, **kwargs):
        print("Repository get_all method called but not implemented")
        pass

    @abstractmethod
    def create(self, *args, **kwargs):
        print("Repository create method called but not implemented")
        pass

    @abstractmethod
    def update(self, *args, **kwargs):
        print("Repository update method called but not implemented")
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        print("Repository delete method called but not implemented")
        pass
