from abc import ABC, abstractmethod
from typing import Any


class BaseComponent(ABC):

    @abstractmethod
    def run(self, *args, **kwargs) -> Any:
        raise NotImplementedError

    @abstractmethod
    async def arun(self, *args, **kwargs) -> Any:
        raise NotImplementedError
