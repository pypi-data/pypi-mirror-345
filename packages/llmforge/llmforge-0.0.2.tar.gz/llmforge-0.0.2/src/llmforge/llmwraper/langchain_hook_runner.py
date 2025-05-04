# """
# WIP DO NOT USE THIS
# """

# from typing import Any, List, Optional, Tuple, Union
# from langchain_core.language_models.chat_models import BaseChatModel
# from langchain_core.messages import BaseMessage, HumanMessage, SystemMessage, AIMessage
# from langchain_core.outputs import ChatGeneration, ChatResult

# from llmforge.llmwraper.models import LLMContext

# from .hooks.base import BaseLLMHook
# from functools import reduce

# class LangChainHookRunner(BaseChatModel):
#     def __init__(self, model: BaseChatModel, hooks: Optional[List[BaseLLMHook]] = None):
#         """model = any LangChain model (ChatOpenAI, ChatAnthropic, etc)"""
#         self.model = model
#         self.hooks = hooks or []
#         self.wrapped_model = self._wrap_model()

#     def llm_type(self) -> str:
#         return "langchain-hook-runner"

#     def _wrap_model(self):
#         """Wrap hooks around the final model call."""
#         return reduce(
#             lambda f, hook: hook(f),
#             reversed(self.hooks),
#             self._base_llm_call
#         )

#     def _base_llm_call(self, ctx: LLMContext) -> LLMContext:
#         """The basic call to the underlying model."""
#         messages: List[BaseMessage] = []
#         if ctx.system_prompt:
#             messages.append(SystemMessage(content=ctx.system_prompt))
#         messages.append(HumanMessage(content=ctx.user_prompt))

#         result: ChatResult = self.model._generate(messages, stop=None)
#         content = self._normalize_content(result.generations[0].message.content)
#         ai_message: AIMessage = AIMessage(content=content)
#         ctx.response_content = content
#         ctx.response = result # type: ignore
#         return ctx

#     def _normalize_content(self, content: Union[str, list[Any]]) -> str:
#         if isinstance(content, list):
#             return "\n".join(str(item) for item in content)
#         return content
    
#     def _generate(self, messages: List[BaseMessage], stop: Optional[List[str]] = None, run_manager=None, **kwargs: Any) -> ChatResult:
#         """This is what LangChain agents will call."""
#         system_prompt, user_prompt = self._extract_prompts(messages)

#         ctx = LLMContext(
#             system_prompt=system_prompt,
#             user_prompt=user_prompt,
#             kwargs=kwargs,
#             model=self.model.__class__.__name__  # or your own naming
#         )

#         ctx = self.wrapped_model(ctx)

#         ai_message = AIMessage(content=ctx.response_content) # type: ignore
#         generation = ChatGeneration(message=ai_message)
#         return ChatResult(generations=[generation])

#     def _extract_prompts(self, messages: List[BaseMessage]) -> Tuple[str, str]:
#         system_prompt = ""
#         user_prompt = ""

#         for msg in messages:
#             if isinstance(msg, SystemMessage):
#                 system_prompt += msg.content # type: ignore
#             elif isinstance(msg, HumanMessage):
#                 user_prompt += msg.content # type: ignore
#         return system_prompt, user_prompt
