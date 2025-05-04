from logging import Logger
from typing import Any, Callable, List, Literal, Optional, Union
import time

import tiktoken

from .base import BaseLLMHook, TLLMContext
from ..models import UsageMetric

class TracingHook(BaseLLMHook):
    def __init__(self, 
                 hook_name: str = "tracing_hook",
                 logger:  Optional[Logger] = None, 
                 usage_metric_parser: Optional[Callable[[Any], UsageMetric]] = None,
                 trace: List[Literal["all", "time", "usage_stats", "model", "model+", "prompts"]] = ["all"],
                 cost_calculator: Optional[Callable[[UsageMetric, str], float]] = None,
                 tiktoken_encoding: Union[str, tiktoken.Encoding] = "o200k_base",
                 verbose: bool = False):
        super().__init__(hook_name, logger, verbose)
        VALID_FIELDS: set[Literal[
            "all", "time", "usage_stats", "model", "model+", 
            "prompts"]] = {"all", "time", "usage_stats", "model", "model+", "prompts"}

        if not all(f in VALID_FIELDS for f in trace):
            raise ValueError(f"Invalid audit field(s): {set(trace) - VALID_FIELDS}")
        self.usage_metric_parser = usage_metric_parser
        self.trace = trace
        self.cost_calculator = cost_calculator
        self.tiktoken_encoding : tiktoken.Encoding
        if isinstance(tiktoken_encoding, str):
            self.tiktoken_encoding = tiktoken.get_encoding(tiktoken_encoding)
        elif isinstance(tiktoken_encoding, tiktoken.Encoding):
            self.tiktoken_encoding = tiktoken_encoding
        else:
            raise ValueError("tiktoken_encoding should be a valid tiktoken model str or a tiktoken.Encoding.")
    
    def __should_trace(self, key: Literal["all", "time", "usage_stats", "model", "model+", "prompts"]) -> bool:
        return "all" in self.trace or key in self.trace
    
    def dispatch(self,  func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            start_time = time.time()
            ctx = func(ctx)
            end_time = time.time()
            elapsed_time = end_time - start_time
            ctx.metadata[self.hook_name] = {}
            ctx.metadata[self.hook_name]["time_taken"] = elapsed_time
            ctx.metadata[self.hook_name]["model_name"] = ctx.model
            
            if self.__should_trace('time'):
                self.log_util(f"[LLM Tracing] Duration: {elapsed_time:.3f}s")
            
            if self.__should_trace("model"):
                self.log_util(f"[LLM Model] model used: {ctx.model}")
            
            if self.__should_trace("usage_stats") and ctx.response:
                if self.usage_metric_parser:
                    usage_metric = self.usage_metric_parser(ctx.response)
                    ctx.metadata[self.hook_name]["usage_metric"] = usage_metric
                    self.log_util(
                        f"[LLM Usage] Input: {usage_metric.input_tokens}, "
                        f"Output: {usage_metric.output_tokens}, "
                        f"Total: {usage_metric.total_tokens}"
                    )
                    if self.cost_calculator:
                        cost = self.cost_calculator(usage_metric, ctx.model)
                        ctx.metadata[self.hook_name]["cost"] = cost
                        self.log_util(f"[LLM Cost] Estimated Cost: ${cost:.4f}")
                else:
                    system_token_count = len(self.tiktoken_encoding.encode(ctx.system_prompt or ""))
                    user_token_count = len(self.tiktoken_encoding.encode(ctx.user_prompt or ""))
                    self.log_util(
                            f"[LLM Usage Tiktoken] Input: {system_token_count + user_token_count},")
                    ctx.metadata[self.hook_name]["usage_metric"] = {"input_token": system_token_count + user_token_count}
            
            if self.__should_trace("prompts"):
                self.log_util(f"[Prompt - System] {ctx.system_prompt}")
                self.log_util(f"[Prompt - User] {ctx.user_prompt}")
            
            if self.__should_trace("model+"):
                self.log_util(f"[LLM Model+] {ctx.kwargs}")
            return ctx
        return wrapper