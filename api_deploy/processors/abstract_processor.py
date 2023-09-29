from abc import ABC, abstractmethod

from api_deploy.config import Config
from api_deploy.schema import Schema


class AbstractProcessor(ABC):

    @abstractmethod
    def __init__(self, config: Config, **kwargs):
        ...

    @abstractmethod
    def process(self, schema: Schema) -> Schema:
        ...
