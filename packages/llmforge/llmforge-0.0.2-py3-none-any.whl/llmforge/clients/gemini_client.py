from typing import Any, List, Optional, Union
from llmforge.llmwraper.base_client import BaseLLMClient
from llmforge.exceptions import EmptyContentError

try:
    from google import genai
except ImportError as e:
    raise ImportError(
        "The `google-generativeai` package is required for `GeminiClient`.\n"
        "Install it with:\n\n"
        "  pip install google-generativeai\n\n"
        "Or pip install .[gemini]"
    ) from e

class GeminiClient(BaseLLMClient):
    def __init__(self, model_name: str, api_key: str, **kwargs):
        super().__init__(model_name)
        self.client = genai.Client(api_key=api_key)
        

    def __call__(self, system_prompt: str, user_prompt: str, *args, **kwargs) -> Any:
        prompt = f"{system_prompt}\n\n{user_prompt}" if system_prompt else user_prompt
        response = self.client.models.generate_content(
                model=self.model_name,
                contents=[prompt]
            )
        return response

    def get_content(self, response_raw: Any) -> str:
        content = getattr(response_raw, "text", None)
        if not content:
            raise EmptyContentError(response_raw)
        return content