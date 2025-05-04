from pydantic import BaseModel, model_validator
from typing import Dict, Literal, Optional, List
from functools import cached_property

class Metadata(BaseModel):
    type: Literal["prompt", "model_prompt"]
    name: str
    description: Optional[str] = None
    tags: Optional[List[str]] = None
    project: Optional[str] = None
    
class Prompt(BaseModel):
    pid: str
    description: Optional[str] = None
    input_variables: Optional[List[str]] = None
    prompt: str

class PromptDataModel(BaseModel):
    pid: str
    description: Optional[str] = None
    input_variables: Optional[List[str]] = None
    model_attribute_id: str
    input_instruction: Optional[str] = None
    output_instruction: Optional[str] = None
    
    @model_validator(mode='after')
    def check_instructions(self) -> "PromptDataModel":
        if not self.input_instruction and not self.output_instruction:
            raise ValueError("Either input_instruction or output_instruction must be provided.")
        return self

class PromptYAMLBase(BaseModel):
    version: float
    metadata: Metadata

class PromptYAML(PromptYAMLBase):
    prompts: List[Prompt]
    
    @cached_property
    def prompt_dict(self) -> dict:
        return {prompt.pid: prompt for prompt in self.prompts}

class PromptDataModelYAML(PromptYAMLBase):
    prompts: List[PromptDataModel]
    
    @cached_property
    def prompt_dict(self) -> Dict:
        return {prompt.pid: prompt for prompt in self.prompts}

    @cached_property
    def prompt_model_dict(self) -> Dict:
        return {prompt.model_attribute_id: prompt for prompt in self.prompts}