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
        # query = kwargs.get("query")
        # check_cache = kwargs.get("check_cache")
        # cache_schema = kwargs.get("cache_schema")
        #
        # if check_cache and self.redis_session is not None:
        #     cached_data = self.redis_session.get(f"{cache_schema.__name__}:{query}")
        #     if cached_data:
        #         return cache_schema.model_load_json(cached_data)
        #
        # queried_object = self.session.scalar(query)
        # if queried_object is not None:
        #     if check_cache and self.redis_session is not None:
        #         self.redis_session.set(f"{cache_schema}:{query}", cache_schema.model_validate(queried_object).model_dump_json())
        #     return queried_object

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
