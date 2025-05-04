from dataclasses import dataclass
from typing import Any, Dict, Generic, List, Literal, Optional
from pydantic import BaseModel
from dataclasses import dataclass, field

@dataclass
class LLMContext:
    system_prompt: str
    user_prompt: str
    model: str
    kwargs: Dict[str, Any] = field(default_factory=dict)
    response: Any = None
    response_content: Optional[str] = None
    parsed_response: Optional[Any] = None  # Keep generic unless strictly typed
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def __post_init__(self):
        if not self.system_prompt or not self.user_prompt:
            raise ValueError("system_prompt and user_prompt must be non-empty.")
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "system_prompt": self.system_prompt,
            "user_prompt": self.user_prompt,
            "model": self.model,
            "kwargs": self.kwargs,
            "response_content": self.response_content,
            "parsed_response": self.parsed_response,
            "metadata": self.metadata,
        }

class UsageMetric(BaseModel):
    input_tokens: int
    output_tokens: int
    total_tokens: int
    raw: dict

Role = Literal["user", "assistant", "extra_context", "tool"]

@dataclass
class Message:
    role: Role
    content: str

@dataclass
class SimpleConversationHistory:
    messages: List[Message] = field(default_factory=list)

    def add(self, role: Role, content: str) -> None:
        self.messages.append(Message(role, content))

    def clear(self) -> None:
        self.messages.clear()

    def format(self) -> str:
        return "\n".join(f"{msg.role.capitalize()}: {msg.content}" for msg in self.messages)

    def last_n(self, n: int) -> str:
        if n >= len(self.messages):
            return self.format()
        return "\n".join(f"{msg.role.capitalize()}: {msg.content}" for msg in self.messages[-n:])

    def __str__(self):
        return self.format()
    def __repr__(self):
        return self.format()
