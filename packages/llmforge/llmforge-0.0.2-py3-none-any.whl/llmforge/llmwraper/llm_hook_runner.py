from functools import reduce
import inspect
from typing import Callable, Dict, List, Union
from .models import LLMContext
from openai import OpenAI
from .base_client import BaseLLMClient
from .hooks.base import BaseLLMHook
from typing import List

class LLMHookRunner:
    def __init__(self, model:  Union[BaseLLMClient, 'LLMHookRunner'], hooks: List[BaseLLMHook], async_mode=True):
        self.model = model # Can be a client or another runner
        self.hooks = hooks
        self.async_mode = async_mode
        self.wrapped_model = self._wrap_model()
        self.model_name = self.get_model_name()

    def get_model_name(self):
        try:
            if isinstance(self.model, BaseLLMClient):
                return self.model.model_name
            elif isinstance(self.model, LLMHookRunner):
                return self.model.get_model_name()
            else:
                raise ValueError("Model must be of type BaseLLMClient or LLMHookRunner")
        except Exception as e:
            raise RuntimeError(f"Failed to get model name: {e}")
    
    def _wrap_model(self):
        try:
            if not all(callable(hook) for hook in self.hooks):
                raise TypeError("All hooks must be callable.")
            return reduce(
                lambda f, hook: hook(f),
                reversed(self.hooks),
                self._llm_call
            )
        except Exception as e:
            raise RuntimeError(f"Failed to wrap model with hooks: {e}")
    
    def _llm_call(self, ctx: LLMContext) -> LLMContext:
        try:
            if not isinstance(ctx, LLMContext):
                raise TypeError("ctx must be an instance of LLMContext.")

            if isinstance(self.model, LLMHookRunner):
                return self.model(ctx.system_prompt, ctx.user_prompt, metadata=ctx.metadata, **ctx.kwargs)  # Delegate to inner runner
            elif isinstance(self.model, BaseLLMClient):
                ctx.response = self.model(
                    system_prompt=ctx.system_prompt,
                    user_prompt=ctx.user_prompt,
                    **ctx.kwargs,
                )
                return ctx
            else:
                raise ValueError("Model must be of type BaseLLMClient or LLMHookRunner")
        except Exception as e:
            raise RuntimeError(f"Failed to execute LLM call: {e}")
    
    def __call__(self, system_prompt: str, user_prompt: str, metadata: Dict = {}, **kwargs) -> LLMContext:
        ctx = LLMContext(
            system_prompt=system_prompt,
            user_prompt=user_prompt,
            kwargs=kwargs,
            model=self.model_name,
            metadata=metadata
        )
        return self.wrapped_model(ctx)
    
    def with_hooks(self, additional_hooks: List[BaseLLMHook]) -> 'LLMHookRunner':
        return LLMHookRunner(
            model=self,  # Chain the current runner
            hooks=additional_hooks,
            async_mode=self.async_mode
        )
    
    def chain(self, additional_hooks: List[BaseLLMHook]) -> 'LLMHookRunner':
        self.hooks.extend(additional_hooks)
        self.wrapped_model = self._wrap_model()
        return self
    
    def update_hooks(self, new_hooks:  List[BaseLLMHook]) -> 'LLMHookRunner':
        self.hooks = new_hooks
        self.wrapped_model = self._wrap_model()
        return self

    def get_content(self, ctx: LLMContext) -> str:
        if not isinstance(ctx, LLMContext):
            raise TypeError("ctx must be an instance of LLMContext.")
        if isinstance(self.model, LLMHookRunner):
            return self.model.get_content(ctx) # Delegate to inner runner
        elif isinstance(self.model, BaseLLMClient):
            return self.model.get_content(ctx.response)
        else:
            raise ValueError("Model must be of type BaseLLMClient or LLMHookRunner")

