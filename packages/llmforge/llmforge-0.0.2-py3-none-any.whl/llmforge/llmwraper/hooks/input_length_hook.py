from logging import Logger
from typing import Callable, Optional, Union

from .base import BaseLLMHook, TLLMContext
from ...exceptions import TokenExceededError
import tiktoken

class InputLengthValidatorHook(BaseLLMHook):
    def __init__(
        self, 
        max_token: int = 6000,
        warn_threshold: float = 0.8,
        tiktoken_encoding: Union[str, tiktoken.Encoding] = "o200k_base",
        hook_name: str = "input_length_hook",
        logger:  Optional[Logger] = None, 
        verbose: bool = False):
        """
        A hook to validate the combined input token length (system + user prompt).
        Raises `TokenExceededError` if it exceeds the configured max_token limit.
        Warns if it exceeds the configured threshold percentage.
        """
        super().__init__(hook_name, logger, verbose)
        self.max_token = max_token
        if warn_threshold > 1 or warn_threshold < 0:
            raise ValueError(f"warn_threshold must be in the range 0 to 1, curently passed value {warn_threshold}")
        self.warn_threshold = warn_threshold
        self.warn_token = self.max_token * self.warn_threshold
        self.tiktoken_encoding : tiktoken.Encoding
        if isinstance(tiktoken_encoding, str):
            self.tiktoken_encoding = tiktoken.get_encoding(tiktoken_encoding)
        elif isinstance(tiktoken_encoding, tiktoken.Encoding):
            self.tiktoken_encoding = tiktoken_encoding
        else:
            raise ValueError("tiktoken_encoding should be a valid tiktoken model str or a tiktoken.Encoding.")

    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            token_count = len(self.tiktoken_encoding.encode(ctx.system_prompt or ""))
            token_count += len(self.tiktoken_encoding.encode(ctx.user_prompt or ""))
            if token_count >= self.warn_token:
                if token_count >= self.max_token:
                    raise TokenExceededError("InputLengthValidatorHook", self.max_token, token_count)
                self.log_util(f"⚠️ Input token exceeded the warning token count of {self.warn_token}, current token count (system + user): {token_count}")
            ctx = func(ctx)
            return ctx
        return wrapper
