import time
from typing import Callable, Literal, Optional, Dict, List, Any, Union

import tiktoken

from llmforge.llmwraper.models import UsageMetric
from .base import BaseLLMHook, TLLMContext

class AuditLogHook(BaseLLMHook):
    def __init__(
        self,
        sink: Callable[[Dict[str, Any]], None],
        audit_fields: List[Literal["all", "time", "usage_stats", "model", "model+", "prompts", "response", "parsed_response"]],
        usage_metric_parser: Optional[Callable[[Any], UsageMetric]] = None,
        extra_data_fn: Optional[Union[Callable[[], Dict[str, Any]], Dict[str, Any]]] = None,
        cost_calculator: Optional[Callable[[UsageMetric, str], float]] = None,
        tiktoken_encoding: Union[str, tiktoken.Encoding] = "o200k_base",
        hook_name: str = "audit_log_hook",
        logger=None,
        verbose=False
    ):
        super().__init__(hook_name, logger, verbose)
        VALID_FIELDS: set[Literal[
            "all", "time", "usage_stats", "model", "model+", 
            "prompts", "response", 
            "parsed_response"]] = {"all", "time", "usage_stats", "model", "model+", "prompts", "response", "parsed_response"}

        if not all(f in VALID_FIELDS for f in audit_fields):
            raise ValueError(f"Invalid audit field(s): {set(audit_fields) - VALID_FIELDS}")
        self.sink = sink
        self.audit_fields = audit_fields
        self.extra_data_fn = extra_data_fn
        self.usage_metric_parser = usage_metric_parser
        self.cost_calculator = cost_calculator
        self.tiktoken_encoding : tiktoken.Encoding
        if isinstance(tiktoken_encoding, str):
            self.tiktoken_encoding = tiktoken.get_encoding(tiktoken_encoding)
        elif isinstance(tiktoken_encoding, tiktoken.Encoding):
            self.tiktoken_encoding = tiktoken_encoding
        else:
            raise ValueError("tiktoken_encoding should be a valid tiktoken model str or a tiktoken.Encoding.")

        
    def __should_log(self, key: Literal["all", "time", "usage_stats", "model", "model+", "prompts", "response", "parsed_response"]) -> bool:
        return "all" in self.audit_fields or key in self.audit_fields
    
    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            start_time = time.time()
            ctx = func(ctx)
            end_time = time.time()
            elapsed_time = end_time - start_time
            audit_log: Dict[str, Any] = {}
            
            if self.__should_log('time'):
                audit_log["time_taken"] = elapsed_time

            if self.__should_log("model"):
                audit_log["model_name"] = ctx.model
                
            if self.__should_log("usage_stats") and ctx.response:
                if self.usage_metric_parser:
                    usage_metric = self.usage_metric_parser(ctx.response)
                    audit_log.update(usage_metric.model_dump())
                    if self.cost_calculator:
                        cost = self.cost_calculator(usage_metric, ctx.model)
                        audit_log["estimated_cost"] = cost
                else:
                    system_token_count = len(self.tiktoken_encoding.encode(ctx.system_prompt or ""))
                    user_token_count = len(self.tiktoken_encoding.encode(ctx.user_prompt or ""))
                    self.log_util(
                            f"[LLM Usage Tiktoken] Input: {system_token_count + user_token_count},")
                    audit_log["input_token"] = system_token_count + user_token_count
            
            if self.__should_log("prompts"):
                audit_log["system_prompt"] = ctx.system_prompt
                audit_log["user_prompt"] = ctx.user_prompt
            
            if self.__should_log("model+"):
                audit_log["extras"] = ctx.kwargs
            
            if self.__should_log("response"):
                audit_log["response"] = ctx.response
                
            if self.__should_log("parsed_response"):
                audit_log["parsed_response"] = ctx.parsed_response
            
            # Append dynamic extra data
            if self.extra_data_fn:
                if isinstance(self.extra_data_fn, Dict):
                    audit_log.update(self.extra_data_fn)
                else:
                    audit_log.update(self.extra_data_fn())
            
            metadata = ctx.metadata.get(self.hook_name, None)
            if metadata and isinstance(metadata, Dict):
                for k, v in metadata.items():
                    if k not in audit_log:
                        audit_log[k] = v
            
            self.sink(audit_log)
            
            self.log_util(f"Audit log generated: {audit_log}")
            
            return ctx

        return wrapper
