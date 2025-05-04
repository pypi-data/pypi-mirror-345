from abc import ABC, abstractmethod
from typing import Any, Optional

class BaseLLMClient(ABC):
    
    def __init__(self, model_name: str):
        super().__init__()
        if not isinstance(model_name, str) or not model_name.strip():
            raise ValueError("model_name must be a non-empty string.")
        self.model_name = model_name
        
    @abstractmethod
    def __call__(self, system_prompt: str, user_prompt: str, *args, **kwargs):
        pass

    @abstractmethod
    def get_content(self, response_raw: Any) -> str:
        pass