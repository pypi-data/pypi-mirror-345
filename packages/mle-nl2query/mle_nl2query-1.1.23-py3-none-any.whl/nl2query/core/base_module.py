from abc import ABC, abstractmethod

from pydantic import BaseModel
from typing import Optional


class BaseModule(ABC):
    """Abstract base class for intent detection engines that process state and output intent JSON"""

    def __init__(
        self,
        pydantic_class: Optional[BaseModel] = None,
        system_prompt: str = None,
        examples: str = None,
        *args,
        **kwargs
    ):
        self.system_prompt = system_prompt
        self.pydantic_class = pydantic_class
        self.examples = examples or []

    @abstractmethod
    def run(self, state):
        pass
