from typing import List, Optional
from openai import OpenAI
from openai.types.chat import ChatCompletionMessageParam, ChatCompletion

from ..llmwraper.base_client import BaseLLMClient
from llmforge.exceptions import EmptyContentError

class OpenAIClient(BaseLLMClient):
    def __init__(self, model_name: str, api_key: str, temperature: float = 0.01, max_retries: int = 1, **kwargs):
        super().__init__(model_name)
        self.temperature = temperature
        self.client = OpenAI(
            api_key=api_key,
            max_retries=max_retries,
            **kwargs
        )

    def __call__(self, system_prompt: str, user_prompt: str, *args, **kwargs) -> ChatCompletion:
        messages: List[ChatCompletionMessageParam] = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        _temperature: float = self.temperature
        if "temperature" in kwargs:
            _temperature = kwargs["_temperature"]
        response = self.client.chat.completions.create(
            messages=messages,
            temperature=_temperature,
            model=self.model_name,
            **kwargs
        )
        return response

    def get_content(self, response_raw: ChatCompletion) -> str:
        content = response_raw.choices[0].message.content
        if not content:
            raise EmptyContentError(response_raw)
        return content
