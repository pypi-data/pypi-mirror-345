from abc import ABC, abstractmethod
from typing import Callable, Optional, TypeVar, Union

from logging import Logger

from ..models import LLMContext

TLLMContext = TypeVar("TLLMContext", bound=LLMContext)

class BaseLLMHook(ABC):
    
    def __init__(self,hook_name: str, logger: Optional[Logger] = None, verbose: bool = False):
        super().__init__()
        self.hook_name = hook_name or self.__class__.__name__
        self.logger = logger
        self.verbose = verbose
    
    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            ctx = self.run_before(ctx)
            ctx = func(ctx)
            ctx = self.run_after(ctx)
            return ctx
        return wrapper

    def run_before(self, ctx: TLLMContext) -> TLLMContext:
        return ctx

    def run_after(self, ctx: TLLMContext) -> TLLMContext:
        return ctx
    
    def log_util(self, msg: str):
        if self.logger:
            self.logger.info(f"{self.hook_name} | {msg}")
        else:
            if self.verbose:
                print(f"{self.hook_name} | {msg}")
    
    def __call__(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        return self.dispatch(func)

    def __init_subclass__(cls, **kwargs):
        super().__init_subclass__(**kwargs)
        if cls.run_before == BaseLLMHook.run_before and cls.run_after == BaseLLMHook.run_after and cls.dispatch == BaseLLMHook.dispatch:
            print(f"⚠️  Warning: {cls.__name__} does not override run_before or run_after or dispatch.")
