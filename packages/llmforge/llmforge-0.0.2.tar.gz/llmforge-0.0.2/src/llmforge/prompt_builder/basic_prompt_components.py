from typing import Dict, List, Optional, Type, Union, cast

from llmforge.models.base import LLMBaseModel
from .base_prompt import BasePromptComponent, catch_keyerror
from ..prompt_hub.models import PromptYAMLBase, PromptYAML, PromptDataModelYAML, Prompt, PromptDataModel
from ..utils import TLLMBaseModel

class SimplePromptComponent(BasePromptComponent):
    class SimplePromptComponent:
        """
        A component for handling simple prompts, which can either be a string or an instance of the `Prompt` class.
        Attributes:
            prompt (Union[str, Prompt]): The prompt content, which can be a plain string or a `Prompt` object.
        Methods:
            render(context: Optional[Dict] = None) -> str:
                Renders the prompt with the given context. If the prompt is a `Prompt` object, it formats the prompt
                string using the provided context. If the prompt is a string, it returns the string as is.
            __repr__() -> str:
                Returns a string representation of the prompt. If the prompt is a `Prompt` object, it delegates to
                the `__repr__` method of the `Prompt` class.
            __str__() -> str:
                Returns the string representation of the prompt. If the prompt is a `Prompt` object, it delegates to
                the `__str__` method of the `Prompt` class.
        """
    def __init__(self, prompt: Union[str, Prompt]):
        self.prompt = prompt

    @catch_keyerror
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if isinstance(self.prompt, Prompt):
            return self.prompt.prompt.format(**context) if context else self.prompt.prompt
        elif isinstance(self.prompt, str):
            return self.prompt
        else:
            raise TypeError(f"Unsupported type for prompt: {type(self.prompt)}")
    
    def __repr__(self):
        if isinstance(self.prompt, Prompt):
            return self.prompt.__repr__()
        elif isinstance(self.prompt, str):
            return self.prompt
        else:
            raise TypeError(f"Unsupported type for prompt: {type(self.prompt)}")
    
    def __str__(self):
        if isinstance(self.prompt, Prompt):
            return self.prompt.__str__()
        elif isinstance(self.prompt, str):
            return self.prompt
        else:
            raise TypeError(f"Unsupported type for prompt: {type(self.prompt)}")


class PromptSectionComponent(BasePromptComponent):
    class PromptSectionComponent:
        """
        A component for building and rendering prompt sections with optional static starting text.
        This class supports rendering prompts from various input types, including strings, 
        `Prompt` objects, and lists of strings or `Prompt` objects. It also provides 
        functionality to prepend a static starting text to the rendered prompt.
        Attributes:
            requirement (Union[str, Prompt, List[str], List[Prompt]]): 
                The main content of the prompt. It can be a single string, a `Prompt` object, 
                a list of strings, or a list of `Prompt` objects.
            static_start (Optional[str]): 
                An optional static text to prepend to the rendered prompt.
        Methods:
            render(context: Optional[Dict] = None) -> str:
                Renders the prompt based on the `requirement` and the provided context. 
                Supports formatting with the context dictionary.
            __repr__() -> str:
                Returns a string representation of the prompt component for debugging purposes.
            __str__() -> str:
                Returns a string representation of the prompt component for display purposes.
        """
    def __init__(self, requirement: Union[str, Prompt, List[str], List[Prompt]], static_start: Optional[str] = None):
        self.requirement = requirement
        self.static_start = static_start

    def __add_static_start(self, _prompt: str) -> str:
        if self.static_start:
            return f"{self.static_start}\n{_prompt}"
        return _prompt

    @catch_keyerror  
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if isinstance(self.requirement, Prompt):
            return self.__add_static_start(self.requirement.prompt.format(**context) if context else self.requirement.prompt)
        elif isinstance(self.requirement, str):
            return self.__add_static_start(self.requirement.format(**context) if context else self.requirement)
        elif isinstance(self.requirement, list):
            if all(isinstance(item, str) for item in self.requirement):
                _prompt: str = "\n- ".join(self.requirement) # type: ignore
                return self.__add_static_start(_prompt.format(**context) if context else _prompt) 
            elif all(isinstance(item, Prompt) for item in self.requirement):
                _prompt: str = "\n- ".join([prompt.prompt for prompt in self.requirement])# type: ignore
                return self.__add_static_start(_prompt.format(**context) if context else _prompt) 
            else:
                raise TypeError("List must contain either all strings or all Prompt objects.")
        else:
            raise TypeError(f"Unsupported type for requirement: {type(self.requirement)}")
    
    def __repr__(self):
        if isinstance(self.requirement, Prompt):
            return self.requirement.__repr__()
        elif isinstance(self.requirement, str):
            return self.requirement
        elif isinstance(self.requirement, list):
            if all(isinstance(item, str) for item in self.requirement):
                return self.__add_static_start("\n- ".join(self.requirement)) # type: ignore
            elif all(isinstance(item, Prompt) for item in self.requirement):
                return self.__add_static_start("\n ".join([prompt.__repr__() for prompt in self.requirement])) # type: ignore
            else:
                raise TypeError("List must contain either all strings or all Prompt objects.")
        else:
            raise TypeError(f"Unsupported type for prompt: {type(self.requirement)}")
    
    def __str__(self):
        if isinstance(self.requirement, Prompt):
            return self.requirement.__str__()
        elif isinstance(self.requirement, str):
            return self.requirement
        elif isinstance(self.requirement, list):
            if all(isinstance(item, str) for item in self.requirement):
                return self.__add_static_start("\n- ".join(self.requirement)) # type: ignore
            elif all(isinstance(item, Prompt) for item in self.requirement):
                return self.__add_static_start("\n- ".join([prompt.__str__() for prompt in self.requirement])) # type: ignore
            else:
                raise TypeError("List must contain either all strings or all Prompt objects.")
        else:
            raise TypeError(f"Unsupported type for prompt: {type(self.requirement)}")


class InputStructureComponent(BasePromptComponent):
    """
    A component for handling input structures in prompt building. This class supports
    various types of input structures, including strings, Prompt objects, and subclasses
    of LLMBaseModel. It provides functionality to render the input structure into a string
    format and optionally prepend a static start string.
    Attributes:
        input_structure (Union[str, Type[TLLMBaseModel], Prompt]): The input structure 
            which can be a string, a Prompt object, or a subclass of LLMBaseModel.
        static_start (Optional[str]): An optional static string to prepend to the rendered
            input structure.
        prompt_model_dict (Optional[Dict[str, PromptDataModel]]): An optional dictionary
            of prompt model data used when rendering input structures of type LLMBaseModel.
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders the input structure into a string format. If a static_start is provided,
            it is prepended to the rendered string. Raises a TypeError if the input structure
            type is unsupported.
        __repr__() -> str:
            Returns a string representation of the input structure. Raises a TypeError if
            the input structure type is unsupported.
        __str__() -> str:
            Returns a string representation of the input structure. Raises a TypeError if
            the input structure type is unsupported.
    """
    def __init__(
        self, input_structure: Union[str, Type[TLLMBaseModel], Prompt], 
        static_start: Optional[str] = None, prompt_model_dict: Optional[Dict[str, PromptDataModel]] = None):
        self.input_structure = input_structure
        self.static_start = static_start
        self.prompt_model_dict = prompt_model_dict

    def __add_static_start(self, _prompt: str) -> str:
        if self.static_start:
            return f"{self.static_start}\n{_prompt}"
        return _prompt

    @catch_keyerror
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if isinstance(self.input_structure, Prompt):
            return self.__add_static_start(self.input_structure.prompt)
        elif isinstance(self.input_structure, str):
            return self.__add_static_start(self.input_structure)
        elif isinstance(self.input_structure, type) and issubclass(self.input_structure, LLMBaseModel):
            return cast(str, self.input_structure.get_input_instructions_with_prompt(
                get_dict=False,
                prompt_model_dict=self.prompt_model_dict
            )) # cast to ignore mypy error: for get_dict=False, the return type is str
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_structure)}")
    
    def __repr__(self):
        if isinstance(self.input_structure, Prompt):
            return self.input_structure.__repr__()
        elif isinstance(self.input_structure, str):
            return self.input_structure
        elif isinstance(self.input_structure, type) and issubclass(self.input_structure, LLMBaseModel):
            return self.input_structure.__repr__()
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_structure)}")
    
    def __str__(self):
        if isinstance(self.input_structure, Prompt):
            return self.input_structure.__str__()
        elif isinstance(self.input_structure, str):
            return self.input_structure
        elif isinstance(self.input_structure, type) and issubclass(self.input_structure, LLMBaseModel):
            return self.input_structure.__str__()
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_structure)}")


class FormatInstructionComponent(BasePromptComponent):
    """
    A component for formatting instructions in a prompt-building context. This class supports
    multiple types of input structures, including strings, Prompt objects, and subclasses of 
    LLMBaseModel. It provides functionality to render the formatted instructions based on the 
    provided input structure and optional static start text.
    Attributes:
        output_structure (Union[str, Type[TLLMBaseModel], Prompt]): The structure of the output 
            instructions. Can be a string, a Prompt object, or a subclass of LLMBaseModel.
        static_start (Optional[str]): Optional static text to prepend to the rendered prompt.
        prompt_model_dict (Optional[Dict[str, PromptDataModel]]): Optional dictionary of prompt 
            data models used for rendering instructions when the output structure is a subclass 
            of LLMBaseModel.
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders the formatted instructions based on the provided context and the type of 
            output structure. Prepends the static start text if provided.
        __repr__() -> str:
            Returns a string representation of the output structure.
        __str__() -> str:
            Returns a string representation of the output structure.
    Raises:
        TypeError: If the type of `output_structure` is unsupported.
    """
    def __init__(
        self, output_structure: Union[str, Type[TLLMBaseModel], Prompt], 
        static_start: Optional[str] = None, prompt_model_dict: Optional[Dict[str, PromptDataModel]] = None):
        self.output_structure = output_structure
        self.static_start = static_start
        self.prompt_model_dict = prompt_model_dict

    def __add_static_start(self, _prompt: str) -> str:
        if self.static_start:
            return f"{self.static_start}\n{_prompt}"
        return _prompt

    @catch_keyerror
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if isinstance(self.output_structure, Prompt):
            return self.__add_static_start(self.output_structure.prompt)
        elif isinstance(self.output_structure, str):
            return self.__add_static_start(self.output_structure)
        elif isinstance(self.output_structure, type) and issubclass(self.output_structure, LLMBaseModel):
            return cast(str, self.output_structure.get_format_instructions_with_prompt(
                get_dict=False,
                prompt_model_dict=self.prompt_model_dict
            )) # cast to ignore mypy error: for get_dict=False, the return type is str
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.output_structure)}")
    
    def __repr__(self):
        if isinstance(self.output_structure, Prompt):
            return self.output_structure.__repr__()
        elif isinstance(self.output_structure, str):
            return self.output_structure
        elif isinstance(self.output_structure, type) and issubclass(self.output_structure, LLMBaseModel):
            return self.output_structure.__repr__()
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.output_structure)}")
    
    def __str__(self):
        if isinstance(self.output_structure, Prompt):
            return self.output_structure.__str__()
        elif isinstance(self.output_structure, str):
            return self.output_structure
        elif isinstance(self.output_structure, type) and issubclass(self.output_structure, LLMBaseModel):
            return self.output_structure.__str__()
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.output_structure)}")
        

class InputComponent(BasePromptComponent):
    """
    A class representing a basic input component for a prompt builder.
    This component allows for the inclusion of a static start message and an input structure
    that can be rendered into a string format for use in prompt generation.
    Attributes:
        static_start (Optional[str]): A static message to prepend to the input component.
            Defaults to "Input for processing is given below.".
        input_component (Optional[str]): The structure of the input component, which can
            include placeholders for dynamic content. Defaults to "<input>{input}</input>".
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders the input component into a string format, optionally using a provided
            context dictionary. Prepends the static start message if it is defined.
        __repr__() -> str:
            Returns a string representation of the input component.
        __str__() -> str:
            Returns a string representation of the input component.
    """
    def __init__(self, static_start: Optional[str] = "Input for processing is given below.", input_component: Optional[str] = "<input>{input}</input>"):
        self.input_component = input_component
        self.static_start = static_start

    def __add_static_start(self, _prompt: str) -> str:
        if self.static_start:
            return f"{self.static_start}\n{_prompt}"
        return _prompt

    @catch_keyerror 
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if isinstance(self.input_component, str):
            return self.__add_static_start(self.input_component)
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_component)}")
    
    def __repr__(self):
        if isinstance(self.input_component, str):
            return self.input_component
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_component)}")
    
    def __str__(self):
        if isinstance(self.input_component, str):
            return self.input_component
        else:
            raise TypeError(f"Unsupported type for input structure: {type(self.input_component)}")


class TemplatePromptComponent(BasePromptComponent):
    """
    A class representing a template-based prompt component that can render
    a string by filling in placeholders with the rendered output of other
    prompt components.
    Attributes:
        template (str): A string template containing placeholders to be filled.
        components (Dict[str, BasePromptComponent]): A dictionary mapping
            placeholder names to their corresponding prompt components.
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders the template by filling in placeholders with the output
            of the corresponding components. If no context is provided, an
            empty dictionary is used.
        __repr__() -> str:
            Returns a string representation of the TemplatePromptComponent
            instance, including its template and components.
        __str__() -> str:
            Returns a user-friendly string representation of the
            TemplatePromptComponent instance, including its template and
            components.
    """
    def __init__(self, template: str, components: Dict[str, BasePromptComponent]):
        self.template = template
        self.components = components

    @catch_keyerror
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        filled_parts = {key: comp.render(context) for key, comp in self.components.items()}
        return self.template.format(**filled_parts)
    
    def __repr__(self):
        return f"TemplatePromptComponent(template={self.template}, components={self.components.__repr__()})"
    
    def __str__(self):
        return f"TemplatePromptComponent(template={self.template}, components={self.components.__str__()})"


class SequentialPromptComponent(BasePromptComponent):
    """
    A class that represents a sequential composition of prompt components. This class
    allows multiple `BasePromptComponent` instances to be combined and rendered in sequence.
    Attributes:
        components (List[BasePromptComponent]): A list of prompt components to be rendered sequentially.
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders all the components in sequence, joining their outputs with double newlines.
            If no context is provided, an empty dictionary is used as the default context.
        __repr__() -> str:
            Returns a string representation of the object for debugging purposes.
        __str__() -> str:
            Returns a user-friendly string representation of the object.
    """
    def __init__(self, components: List[BasePromptComponent]):
        self.components = components
    
    @catch_keyerror
    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        return "\n\n".join(component.render(context) for component in self.components)
    
    def __repr__(self):
        return f"ChainedPromptComponent(components={self.components.__repr__()})"

    def __str__(self):
        return f"ChainedPromptComponent(components={self.components.__str__()})"


class ConditionalPromptComponent(BasePromptComponent):
    """
    A prompt component that conditionally renders another component based on a context key.
    This class wraps another `BasePromptComponent` and renders it only if a specified
    condition key exists and evaluates to a truthy value in the provided context.
    Attributes:
        component (BasePromptComponent): The prompt component to be conditionally rendered.
        condition_key (str): The key in the context dictionary that determines whether
            the component should be rendered.
    Methods:
        render(context: Optional[Dict] = None) -> str:
            Renders the wrapped component if the condition key in the context is truthy.
            Returns an empty string otherwise.
        __repr__() -> str:
            Returns a string representation of the ConditionalPromptComponent, including
            the condition key and the wrapped component.
        __str__() -> str:
            Returns a human-readable string representation of the ConditionalPromptComponent,
            including the condition key and the wrapped component.
    """
    def __init__(self, component: BasePromptComponent, condition_key: str):
        self.component = component
        self.condition_key = condition_key

    def render(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        if context.get(self.condition_key):
            return self.component.render(context)
        return ""
    
    def __repr__(self):
        return f"ConditionalComponent(condition_key={self.condition_key}, component={self.component.__repr__()})"

    def __str__(self):
        return f"ConditionalComponent(condition_key={self.condition_key}, component={self.component.__str__()})"
