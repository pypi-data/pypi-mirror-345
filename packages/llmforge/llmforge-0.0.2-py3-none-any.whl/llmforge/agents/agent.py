from datetime import datetime, timezone
import inspect
import time
from typing import Callable, Dict, Any, List, Optional, Type, Union
from functools import partial
from llmforge.agents.models import ( 
    AgentScratchStep,
    AgentHistoryItem,
    IntermediateAgentInput,
    IntermediateAgentOutput,
    Tool,
    LLMToolsInput
)
from llmforge.exceptions import OutputParsingError
from llmforge.llmwraper.hooks.base import BaseLLMHook
from llmforge.llmwraper.models import SimpleConversationHistory
from llmforge.prompt_hub.models import PromptDataModel
from llmforge.utils import TLLMBaseModel
from llmforge.parsers import pydantic_parser
from llmforge.llmwraper import LLMHookRunner, BaseLLMClient

class LLMReActAgent:
    def __init__(self, 
                 tools: Union[Dict[str, Tool], List[Tool], List[Callable[..., str]], Dict[str, Callable[..., str]]], 
                 llm: Union[BaseLLMClient, LLMHookRunner, Callable[[str, str], str]],
                 task_definition: str,
                 hooks: List[BaseLLMHook] = [],
                 agent_input_schema: Optional[str] = None,
                 final_output_model: Optional[Type[TLLMBaseModel]] = None,
                 output_model_dict: Optional[Dict[str, PromptDataModel]] = None,
                 max_steps: int = 10,
                 max_time: int = 60, # 60 second
                 verbose: bool = False
                 ):
        if not tools:
            raise ValueError(f"No tools passed to agent: {__name__}")
        if not task_definition:
            raise ValueError(f"Agent: {__name__} needs task definition to work properly.")
        
        self.llm: Union[LLMHookRunner, Callable[[str, str], str]] = self.__get_llm(
            llm=llm,
            hooks=hooks
        )
        self.task_definition = task_definition
        self.agent_input_schema = agent_input_schema
        self.final_output_model = final_output_model
        self.output_model_dict = output_model_dict
        self.max_steps = max_steps
        self.verbose = verbose
        self.max_time = max_time
        self.general_instruction_system = (
            "You are an intelligent agent that completes complex tasks by thinking step-by-step.\n"
            "You have access to external tools to help you complete the task.\n"
            "\n"
            "You MUST always reason before using a tool.\n"
            "If you are still reasoning and not ready to invoke a tool, set `is_reasoning` to True.\n"
            "In this case, leave the `action` and `action_input` fields as None. Do not specify a tool name yet.\n"
            "When you are sure and ready to choose a tool, set `is_reasoning` to False.\n"
            "Then, provide the tool name in `action`, a valid input dictionary in `action_input`, and describe what you expect from the tool in `expectation`.\n"
            "The tool will only be executed when `is_reasoning` is False.\n"
            "\n"
            "Each step of tool usage, including the tool name, input, and result, is tracked in the tool history.\n"
            "You must check the tool history before repeating a tool call with the same input argument to avoid redundant actions.\n"
            "\n"
            "You are also given a conversation history between the user and assistant.\n"
            "Use the conversation history to:\n"
            "- Reuse previous final answers if the current question is the same or highly similar.\n"
            "- Maintain context across the conversation. For example, interpret phrases like 'that place' based on earlier references.\n"
            "- Avoid asking the user to repeat information already provided.\n"
            "\n"
            "If the user's current question is incomplete or missing critical details:\n"
            "- First, try to infer the missing details from the conversation history.\n"
            "- If essential details are still missing and cannot be inferred, set `is_reasoning` to True and clearly explain what specific information is required to proceed.\n"
            "- In the `final_answer` field, ask the user for that specific clarification in a clear and natural way (e.g., 'Could you specify which product you're referring to?' or 'What location do you mean by 'there'?').\n"
            "\n"
            "If the user's question is ambiguous but potentially answerable in more than one way:\n"
            "- These partial ambiguities can involve the interpretation of place, time, names, or entities that may have multiple meanings depending on context.\n"
            "- Proceed with reasoning and tool use based on the most likely interpretation.\n"
            "- In the `final_answer`, provide the response **based on the interpretation you chose**,  after you have completed your reasoning and clearly mention the ambiguity.\n"
            "- Ask the user to confirm or clarify what they meant (e.g., 'Did you mean the programming language or the snake when you said Python?').\n"
            "\n"
            "If the current question appears answerable but requires specific tool use or context confirmation, reason through it carefully, check history/tool outputs, and act accordingly.\n"
            "\n"
            "If the question cannot be answered due to missing information, ambiguity, or limitations in your tools or knowledge:\n"
            "- Clearly state that the answer cannot be provided yet and explain why.\n"
            "- Mention any assumptions you've made if partial reasoning is possible.\n"
            "- Optionally ask the user a clarifying question to proceed.\n"
            
        )
        self.system_prompt_parts = [self.general_instruction_system, f"Your task is: {self.task_definition}"]
        if self.agent_input_schema:
            self.system_prompt_parts.append(f"User question/input will come in structured format, and that input definition is: {self.agent_input_schema}")        
        self.system_prompt_parts.append(f"""
        You will be given few tools to provide the answer to user question. 
        Avilable tools will be given in structured format, 
        below instruction provides semantic representation of input tools fields. \n{LLMToolsInput.get_input_instructions(ignore=("LLMToolsInput.Tool.tool",))}""")
        self.system_prompt_parts.append(f"""
        You will be given a history of your actions taken already to answer the users question in structured format,
        below instruction provides semantic representation of the history fields. \n{IntermediateAgentInput.get_input_instructions()}""")
        self.system_prompt_parts.append(
            f"""You are executing this task on {datetime.now(timezone.utc)} UTC. 
            Use this date to verify claims, timelines, and whether previous tool results are outdated. 
            Treat tool results as potentially stale if they conflict with known facts based on the current date."""
        )
        self.system_prompt = "\n\n".join(self.system_prompt_parts)
        
        self.tools_input = tools
        self.tools = self.__get_tools(self.tools_input)
        self.tools_llm_input = LLMToolsInput(
            tools=list(self.tools.values())
        )
        
        self.general_instruction_user = (
            # "Your goal is to help answer the user's question by reasoning through the problem, using tools when necessary.\n"
            # "Think step-by-step and call a tool when you need external information or computation.\n"
            # "Each time you call a tool, its result is stored in the history. Use that history to avoid repeating actions.\n"
            # "Only give your final answer when you are fully confident and have gathered all necessary tool results.\n"
            ""
        )
        self.user_prompt_parts = [self.general_instruction_user, 
                                "Conversation so far:\n{conversation_history}", 
                                "Available tools: {tools}",
                                "History of your actions: {history}",
                                "User question: {question}"]
        if self.final_output_model:
            self.user_prompt_parts.append("""If you have reached you final ans then in IntermediateAgentOutput.
                                          final_answer you give your answer. 
                                          Format isntructions for the final answer: \n {final_answer_format}.
                                          ######""")
        else:
            self.user_prompt_parts.append("""Format the final answer as clean, concise plain text with no markdown, emojis, or decorative characters. 
                                   Use full sentences and structured paragraphs. If listing items, 
                                   use numbered or bulleted lists with consistent spacing. Avoid repeating information. 
                                   The final answer should look like it belongs in a professional report or UI display.
                                   ######""")
        self.user_prompt_parts.append("The output should STRICTLY FOLLOW: {format_instructions}")
        self.user_prompt = "\n\n".join(self.user_prompt_parts)
        self.intermediate_parser = partial(pydantic_parser,model=IntermediateAgentOutput)
        if self.verbose:
            print(f"Initialized LLMToolAgent with tools: {list(self.tools.keys())}")

    def __get_llm(self, 
                       llm: Union[BaseLLMClient, LLMHookRunner, Callable[[str, str], str]], 
                       hooks: List[BaseLLMHook]) -> Union[LLMHookRunner, Callable[[str, str], str]]:
        if isinstance(llm, LLMHookRunner):
            return llm
        elif isinstance(llm, BaseLLMClient):
            return LLMHookRunner(model=llm, hooks=hooks)
        elif callable(llm):
            sig = inspect.signature(llm)
            params = list(sig.parameters.values())

            if len(params) != 2 or any(p.annotation not in (str, inspect._empty) for p in params):
                raise TypeError("Callable must accept exactly two string arguments.")
            return llm
        else:
            raise TypeError(
                f"Invalid LLM type: {type(llm).__name__}. "
                "Expected BaseLLMClient, LLMHookRunner, or a callable object."
            )
    
    def __get_tools(self, tools_input: Union[Dict[str, Tool], List[Tool], List[Callable[..., str]], Dict[str, Callable[..., str]]]) -> Dict[str, Tool]:
        tools: Dict[str, Tool] = {}

        if isinstance(tools_input, dict):
            for key, val in tools_input.items():
                if isinstance(val, Tool):
                    tools[val.tool_name] = val
                elif callable(val):
                    tool = Tool.from_function(val)
                    tools[tool.tool_name] = tool
                else:
                    raise ValueError(f"Unsupported tool type for key '{key}': {type(val)}")
        elif isinstance(tools_input, list):
            for item in tools_input:
                if isinstance(item, Tool):
                    tools[item.tool_name] = item
                elif callable(item):
                    tool = Tool.from_function(item)
                    tools[tool.tool_name] = tool
                else:
                    raise ValueError(f"Unsupported tool type in list: {type(item)}")
        else:
            raise TypeError(f"Invalid type for tools_input: {type(tools_input)}")

        return tools
    
    def run(self, 
            question: str, 
            conversation_history: Optional[SimpleConversationHistory] = None,
            conversation_last_n: int = 10,
            metadata: Optional[Dict] = None) -> str:
        input_state = IntermediateAgentInput(
            is_last_step_reasoning= True,
            last_tool_called=None,
            last_tool_args=None,
            last_tool_result="Let me reason first.",
            history=[]
        )
        
        start_time = time.time()
        step = 0
        while step < self.max_steps and time.time() - start_time <= self.max_time:
            step += 1
            if self.verbose:
                print(f"\n🔁 Step {step} -------------------------")
                print(f"Current history: {input_state.model_dump_json()}")
            
            try:
                output = self._agent_step(question, input_state, conversation_history, conversation_last_n, metadata)
                if self.verbose:
                    print(f"✅ LLM parsed output: {output}")
            except OutputParsingError as e:
                # logger.warning(f"Parsing failed at step {step}: {e}")
                print(f"❌ Parsing failed at step {step}: {e}")
                continue
            except Exception as e:
                print(f"❌ Error at {step}: {e}")
                continue

            if output.final_answer:
                if self.verbose:
                    print(f"✅ Final answer reached at step {step}: {output.final_answer}")
                return output.final_answer
            else:
                # comment: 
                if self.verbose:
                    print(f"⚠️ Final answer not reached at step {step}, continuing!")
            tool_name = output.current_scratchpad.action
            tool_input = output.current_scratchpad.action_input or {}
            
            if output.current_scratchpad.is_reasoning:
                # model is reasoning
                if self.verbose:
                    print(f"🔧 Model is reasiong and chose '{tool_name}' with input: {tool_input}, with reason: {output.current_scratchpad.thought}")
                result = f"Model is currently in reasoning loop with thought: {output.current_scratchpad.thought}"
            else:
                
                if not tool_name:
                    # logger.warning(f"Step {step}: Missing tool name. Skipping execution.")
                    print(f"⚠️ Step {step}: Missing tool name. Skipping execution.")
                    continue
                tool = self.tools.get(tool_name)
                if not tool:
                    # logger.warning(f"Step {step}: Unknown tool '{tool_name}'. Skipping execution.")
                    print(f"⚠️ Step {step}: Unknown tool '{tool_name}'. Skipping execution.")
                    continue  # 💡 Skip tool error instead of crashing
                if self.verbose:
                    print(f"🔧 Executing tool '{tool_name}' with input: {tool_input}")
                try:
                    result = tool.tool(**tool_input)
                    if self.verbose:
                        print(f"✅ Tool '{tool_name}' result: {result}")
                except Exception as e:
                    # logger.warning(f"Step {step}: Tool '{tool_name}' execution failed: {e}")
                    print(f"❌ Step {step}: Tool '{tool_name}' execution failed: {e}")
                    result = f"Error during tool execution: {e}"

            input_state.history.append(AgentHistoryItem(
                scratchpad=output.current_scratchpad,
                result=result
            ))
            input_state.last_tool_called = tool_name
            input_state.last_tool_args = tool_input
            input_state.last_tool_result = result
        
        raise TimeoutError(f"⏰ Agent exceeded max steps ({self.max_steps}) without reaching a final answer.")

    def _agent_step(self, 
                    question: str, 
                    input_state: IntermediateAgentInput,
                    conversation_history: Optional[SimpleConversationHistory] = None,
                    conversation_last_n: int = 10,
                    metadata: Optional[Dict] = None) -> IntermediateAgentOutput:

        if self.final_output_model:
            prompt = self.user_prompt.format(
                question=question, 
                history=input_state.model_dump_json(),
                tools=self.tools_llm_input.model_dump_json(),
                final_answer_format=self.final_output_model.get_format_instructions_with_prompt(prompt_model_dict=self.output_model_dict),
                format_instructions = str(IntermediateAgentOutput.get_format_instructions()),
                conversation_history=conversation_history.last_n(conversation_last_n) if conversation_history else "No conversation history provided"
                )
        else:
            prompt = self.user_prompt.format(
                question=question, 
                history=input_state.model_dump_json(),
                tools=self.tools_llm_input.model_dump_json(),
                format_instructions = str(IntermediateAgentOutput.get_format_instructions()),
                conversation_history=conversation_history.last_n(conversation_last_n) if conversation_history else "No conversation history provided"
                )
        
        if isinstance(self.llm, (LLMHookRunner)):
            llm_response_ctx = self.llm(
                system_prompt=self.system_prompt,
                user_prompt=prompt,
                metadata=metadata if metadata else {}
            )
            content = self.llm.get_content(llm_response_ctx)
        elif callable(self.llm):
            try:
                result = self.llm(self.system_prompt, prompt)

                if not isinstance(result, str):
                    raise TypeError("Callable must return a string.")

                content = result

            except Exception as e:
                raise TypeError(f"Invalid callable LLM. Expected Callable[[str, str], str]. Got error: {e}")
        else:
            raise TypeError(
                        f"Invalid LLM type: {type(self.llm).__name__}. "
                        "Expected BaseLLMClient, LLMHookRunner, or a callable object."
                    )
        
        if self.verbose:
            print(f"📨 LLM raw response:\n{content}\n")
        
        return self.intermediate_parser(llm_response_content=content)
