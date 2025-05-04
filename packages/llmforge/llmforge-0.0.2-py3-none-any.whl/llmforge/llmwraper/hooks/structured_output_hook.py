from logging import Logger
from typing import Callable, Optional, Tuple, Type

from .base import BaseLLMHook, TLLMContext
from ...utils import TLLMBaseModel
from ...parsers import json_parser, pydantic_parser


class PydanticOutputHook(BaseLLMHook):
    def __init__(self, 
                pydantic_model: Type[TLLMBaseModel],
                parse: bool = True,
                hook_name: str = "structured_output_hook",
                logger:  Optional[Logger] = None, 
                verbose: bool = False):
        super().__init__(hook_name, logger, verbose)
        self.pydantic_model = pydantic_model
        self.parse = parse
    
    def dispatch(self, func):
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            ctx = func(ctx)
            if ctx.response_content and isinstance(ctx.response_content, str):
                parsed_data = pydantic_parser(ctx.response_content, self.pydantic_model)
                if self.parse:
                    ctx.parsed_response = parsed_data
            else:
                self.log_util(f"No Response found to parse, response {ctx.response_content}")
            return ctx 
        return wrapper 


class JSONParserHook(BaseLLMHook):
    def __init__(self, 
                hook_name: str = "structured_output_hook",
                logger:  Optional[Logger] = None, 
                verbose: bool = False):
        super().__init__(hook_name, logger, verbose)
    
    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            ctx = func(ctx)
            if ctx.response_content and isinstance(ctx.response_content, str):
                parsed_data = json_parser(ctx.response_content)
                ctx.parsed_response = parsed_data
            else:
                self.log_util(f"No Response found to parse, response {ctx.response_content}")
            return ctx
        return wrapper
