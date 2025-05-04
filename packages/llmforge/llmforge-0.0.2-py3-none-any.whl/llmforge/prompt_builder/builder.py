from typing import Dict, List, Optional

from .base_prompt import BasePromptComponent

class StructuredPromptBuilder:
    def __init__(self):
        self.components: List[BasePromptComponent] = [] # type: ignore
    
    def add(self, component: BasePromptComponent) -> "StructuredPromptBuilder":
        """
        Add a prompt component to the builder.
        """
        self.components.append(component)
        return self
    
    def __rshift__(self, other) -> "StructuredPromptBuilder":
        """
        Add a prompt component to the builder using the `>>` operator.
        """
        if isinstance(other, BasePromptComponent):
            return self.add(other)
        raise TypeError(f"Cannot '>>' {type(other)} into prompt builder")
    
    def __or__(self, other) -> "StructuredPromptBuilder":
        """
        Add a prompt component to the builder using the `|` operator.
        """
        if isinstance(other, BasePromptComponent):
            return self.add(other)
        raise TypeError(f"Cannot pipe {type(other)} into prompt builder")

    def build(self, context: Optional[Dict] = None) -> str:
        if context is None:
            context = {}
        return "\n\n".join([c.render(context) for c in self.components])
    
    def render_preview(self, context: Optional[Dict] = None, show_index: bool = True) -> None:
        if context is None:
            context = {}
        print("🔍 Prompt Preview:\n" + "=" * 30)
        for i, component in enumerate(self.components):
            rendered = component.render(context)
            index_label = f"[{i}] " if show_index else ""
            print(f"{index_label}{rendered}\n{'-' * 30}")