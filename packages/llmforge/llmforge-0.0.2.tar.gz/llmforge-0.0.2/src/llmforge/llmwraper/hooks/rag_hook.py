from typing import Callable, List, Optional, Union, Dict, Any, Type
import json
from llmforge.models.base import LLMBaseModel
from llmforge.prompt_hub.models import PromptDataModel
from llmforge.utils import TLLMBaseModel
from .base import BaseLLMHook, TLLMContext


class RAGHook(BaseLLMHook):
    def __init__(
        self,
        retriever: Callable[[str], List[Union[str, Dict[str, Any]]]],
        output_schema: Optional[Union[Type[TLLMBaseModel], str]] = None,
        output_schema_prompt_dict: Optional[Dict[str, PromptDataModel]] = None,
        prompt_prefix: str = "",
        promt_sufix: str = "",
        hook_name: str = "rag_hook",
        logger=None,
        verbose=False
    ):
        super().__init__(hook_name, logger, verbose)
        self.template = prompt_prefix + "Use the following context:\n<context>{context}</context>\n\nAnswer the question:\n<question>{question}</question>" + promt_sufix
        if output_schema:
            if isinstance(output_schema, str):
                self.template += f"\n\n{output_schema}"
            elif isinstance(output_schema, type) and issubclass(output_schema, LLMBaseModel):
                self.template += f"\n\n{output_schema.get_format_instructions_with_prompt(
                    get_dict=False, 
                    prompt_model_dict=output_schema_prompt_dict)}"
            else:
                raise ValueError("output_schema must be a str or a TLLMBaseModel")

        self.prompt_prefix = prompt_prefix
        self.prompt_sufix = promt_sufix
        self.retriever = retriever
        self.output_schema = output_schema
        self.output_schema_prompt_dict = output_schema_prompt_dict

    def dispatch(self, func: Callable[[TLLMContext], TLLMContext]) -> Callable[[TLLMContext], TLLMContext]:
        def wrapper(ctx: TLLMContext) -> TLLMContext:
            question = ctx.user_prompt
            chunks = self.retriever(question)
            
            self.log_util(f"Chunks received for question: '{question}',  are: {chunks}")
            
            if all(isinstance(chunk, str) for chunk in chunks):
                context_str = "\n\n".join(chunks) # type: ignore
            else:
                context_str = json.dumps(chunks, indent=2)
            
            formatted_prompt = self.template.format(context=context_str, question=question)
            ctx.user_prompt = formatted_prompt
            
            return func(ctx)

        return wrapper
