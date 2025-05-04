from typing import TypeVar, Generic
from .models import LLMBaseModel

TLLMBaseModel = TypeVar("TLLMBaseModel", bound=LLMBaseModel)