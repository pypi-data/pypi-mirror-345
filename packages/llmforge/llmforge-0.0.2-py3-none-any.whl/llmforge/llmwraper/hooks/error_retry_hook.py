from logging import Logger
import random
import time
from typing import Callable, Optional, Tuple, Type

from .base import BaseLLMHook, TLLMContext

class ErrorRetryHook(BaseLLMHook):
    def __init__(self, 
                 hook_name: str = "error_retry_hook",
                 retries: int = 3,
                 retry_exceptions: Tuple[Type[BaseException], ...] = (Exception,),
                 delay: bool = False,
                 base_delay: float = 0.5,
                 max_delay: float = 5,
                 logger:  Optional[Logger] = None, 
                 verbose: bool = False):
        super().__init__(hook_name, logger, verbose)
        self.retries = retries
        self.retry_exceptions = retry_exceptions
        self.delay = delay
        self.base_delay = base_delay
        self.max_delay = max_delay
    
    def __get_delay(self, attempt: int) -> float:
        if not self.delay:
            return 0.0
        _delay = min(self.max_delay, self.base_delay * (2 ** (attempt - 1))) # exponential delay
        jitter = random.uniform(0, _delay * 0.1)
        return _delay + jitter
    
    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            for attempt in range(1, self.retries + 1):
                try:
                    return func(ctx)
                except self.retry_exceptions as e:
                    if attempt == self.retries:
                        self.log_util(f"Final attempt {attempt} failed with {type(e).__name__}: {e}")
                        raise e
                    delay = self.__get_delay(attempt)
                    self.log_util(f"Attempt {attempt} failed with {type(e).__name__}: {e}. Retrying in {delay:.2f}s...")
                    time.sleep(delay)
            return ctx # unreachable due to raise 
        return wrapper
