import inspect
from typing import Annotated, Any, Dict, List, Callable, Optional, Type, Union, cast
from pydantic import BaseModel, Field

from llmforge.models import LLMBaseModel,LLMField

class ToolAttribute(LLMBaseModel):
    name: str = LLMField(..., input_instruction="The name of a single input parameter required by the tool.")
    type: str = LLMField(..., input_instruction="The data type of this parameter (e.g., 'str', 'int', 'bool').")
    description: str = LLMField(..., input_instruction="A natural language explanation of what this parameter represents and how it should be used.")
    required: bool = LLMField(True, input_instruction="Indicates whether this input is required (True) or optional (False) when calling the tool.")
    default_value: Optional[Any] = LLMField(None, input_instruction="The default value used if this parameter is optional and not provided.")

class Tool(LLMBaseModel):
    tool_name: str = LLMField(..., input_instruction="The name of the tool. This is a unique identifier used to refer to this tool when invoking it.")
    tool: Callable[..., str] = LLMField(..., input_instruction="The callable implementation of the tool (not used by the LLM directly). | This will be ignored.", exclude=True)
    tool_description: str = LLMField(..., input_instruction="A high-level natural language description of what the tool does and when it should be used.")
    tool_signature: str = LLMField(..., input_instruction="The full Python function signature of the tool, including parameter names and types.")
    input_attributes: List[ToolAttribute] = LLMField(..., input_instruction="A list of input parameters that the tool expects, with names, types, and descriptions for each.")
    
    @classmethod
    def from_function(cls, 
                      tool: Callable[..., str], 
                      input_attributes: Optional[List[ToolAttribute]] = None,
                      arg_descriptions: Optional[Dict[str, str]] = None,
                      raise_on_no_annotation: bool = True) -> 'Tool':
        
        sig = inspect.signature(tool)
        parameters = list(sig.parameters.values())

        # If it's a bound method, remove 'self' or 'cls'
        if inspect.ismethod(tool) and parameters and parameters[0].name in {"self", "cls"}:
            parameters = parameters[1:]

        attributes = list(input_attributes) if input_attributes else []
        if not input_attributes:
            for param in parameters:
                description = ""
                param_type = "Any"

                if arg_descriptions and param.name in arg_descriptions:
                    description = arg_descriptions[param.name]

                if param.annotation == inspect._empty:
                    if raise_on_no_annotation:
                        raise ValueError(f"Parameter '{param.name}' has no type annotation.")
                elif hasattr(param.annotation, "__origin__") and param.annotation.__origin__ is Annotated:
                    # Handle Annotated types
                    args = param.annotation.__args__
                    if len(args) > 0 and isinstance(args[0], type):
                        param_type = args[0].__name__  # Base type (e.g., int, str, etc.)
                    description = ".\n".join(str(arg) for arg in args[1:]) if len(args) > 1 else ""
                else:
                    param_type = param.annotation.__name__ if isinstance(param.annotation, type) else str(param.annotation)

                required = param.default == inspect.Parameter.empty
                default_value = None if required else param.default
                
                attributes.append(
                    ToolAttribute(
                        name=param.name,
                        type=param_type,
                        description=description,
                        required=required,
                        default_value=default_value
                    )
                )

        return cls(
            tool_name=get_callable_name(tool),
            tool=tool,
            tool_description=inspect.getdoc(tool) or "No description provided.",
            tool_signature=str(sig),
            input_attributes=attributes
        )
        
def get_callable_name(tool: Callable) -> str:
    if inspect.ismethod(tool):
        cls_name = tool.__self__.__class__.__name__
        return f"{cls_name}.{tool.__func__.__name__}"
    elif inspect.isfunction(tool):
        return tool.__name__
    elif hasattr(tool, '__call__'):
        call_attr = getattr(tool, '__call__', None)
        if inspect.ismethod(call_attr):
            cls_name = call_attr.__self__.__class__.__name__
            return f"{cls_name}.{call_attr.__func__.__name__}"
        elif inspect.isfunction(call_attr):
            return call_attr.__name__
    return tool.__class__.__name__

class LLMToolsInput(LLMBaseModel):
    tools: List[Tool] = LLMField(..., input_instruction="A list of all available tools you can choose from. Each tool includes its name, description, signature, and input parameters.")

class AgentScratchStep(LLMBaseModel):
    """One step of the agent's reasoning loop."""
    thought: str = LLMField(
        ..., 
        input_instruction="Provided as the agent's initial reflection or reasoning at this step.",
        output_instruction="Describe the agent's internal reflection before selecting any tool or action."
    )
    is_reasoning: bool = LLMField(
        ...,
        input_instruction="Here it is mentioned if in this step LLM decided on any Tool or it is reasoning with itself.",
        output_instruction="""Use is_reasoning: true when still deciding. Use is_reasoning: false when ready to invoke tool
        Set this to true if you are not ready to choose this tool and want to reason more before deciding to choose the tool and the input, 
        you current choicees made here will be given to you in the next loop."""
    )
    action: Optional[str] = LLMField(
        None,
        input_instruction="Provided as the name of the tool the agent attempted to use, if any.",
        output_instruction="""If a tool is to be used, provide the tool's name exactly as defined in the Available tools section; 
        If you have reached the final answer, output 'completed'. 
        If you don't know what tool to use, output 'unknown'."""
    )
    action_input: Optional[Dict[str, Any]] = LLMField(
        None,
        input_instruction="Provided as a dictionary of arguments passed to the chosen tool.",
        output_instruction="Specify a dictionary containing the required parameters for the selected tool."
    )
    expectation: Optional[str] = LLMField(
        None,
        input_instruction="What the agent expected as output from the selected tool for this action.",
        output_instruction="What the expected output, required from the selected tool."
    )

class AgentHistoryItem(LLMBaseModel):
    """Agent action history and results."""
    scratchpad: AgentScratchStep = LLMField(
        ..., 
        input_instruction="A record of the agents thoughts, actions, and observations for a past step."
    )
    result: str = LLMField(
        ..., 
        input_instruction="The final output received or generated as a result of the scratchpad step."
    )

class IntermediateAgentInput(LLMBaseModel):
    """What the agent sees at the start of a reasoning loop."""
    is_last_step_reasoning: bool = LLMField(
        ..., 
        input_instruction="This indicates if last loop was a reasioning loop. If reasoning then the tool mentioned here are not invoked, it is mearly what tentative tool agent choose in last step. Reason of choosing is in the result section in that case."
    )
    last_tool_called: Optional[str] = LLMField(
        None, 
        input_instruction="The name of the most recently used tool, or None if no previous tool was used."
    )
    last_tool_args: Optional[Dict[str, Any]] = LLMField(
        None, 
        input_instruction="A dictionary of arguments passed to the most recently used tool."
    )
    last_tool_result: Optional[str] = LLMField(
        None, 
        input_instruction="The result or output produced by the last tool call."
    )
    history: List[AgentHistoryItem] = LLMField(
        default_factory=list,
        input_instruction="A list of all previous reasoning steps, including tool usage and their outcomes."
    )


class IntermediateAgentOutput(LLMBaseModel):
    """What the agent generates at the end of a reasoning loop iteration."""
    current_scratchpad: AgentScratchStep = LLMField(
        ..., 
        output_instruction="Provide the next step of the agent's reasoning process, including tool usage."
    )
    final_answer: Optional[str] = LLMField(
        None, 
        output_instruction="If the agent has reached a conclusion, return the final answer here; otherwise, leave blank."
    )
