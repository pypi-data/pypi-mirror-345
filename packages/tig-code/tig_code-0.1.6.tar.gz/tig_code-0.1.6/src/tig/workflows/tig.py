import re
from typing import Dict, List, Any

from llama_index.core.llms.llm import LLM
from llama_index.core.llms import ChatMessage
from llama_index.core.workflow import (
    step,
    Context,
    Workflow,
    Event,
    StartEvent,
    StopEvent,
)
from tig.modes import MODES
from tig.utils.xml import parse_tool_call
from tig.prompts.system import get_system_prompt
from tig.prompts.environment import get_environment_reminder_prompt
from tig.tools import (
    list_files,
    ask_followup_questions,
    list_code_definitions,
    read_file,
    regex_search_files,
    write_to_file,
    apply_diff,
    execute_command,
)

ANSI_GREEN = "\033[32m"
ANSI_RESET = "\033[0m"


class NewTaskCreated(Event):
    pass


class PromptGenerated(Event):
    prompt: str
    is_system_prompt: bool = False


class LLMResponded(Event):
    response: str


class ToolCallRequired(Event):
    tool: Dict


class TigWorkflow(Workflow):
    def __init__(
        self,
        *args: Any,
        llm: LLM,
        mode: str,
        auto_approve: bool = False,
        verbose_prompt: bool = False,
        **kwargs: Any,
    ) -> None:
        super().__init__(*args, **kwargs)
        self.llm = llm
        if mode not in MODES:
            raise ValueError(f"Invalid mode: {mode}")
        self.mode = mode
        self.chat_history: List[ChatMessage] = []
        self.auto_approve = auto_approve
        self.verbose_prompt = verbose_prompt

    @step
    async def start_new_task(self, ctx: Context, ev: StartEvent) -> NewTaskCreated:
        task = ev.get("task")
        await ctx.set("task", task)
        return NewTaskCreated()

    @step
    async def generate_system_prompt(
        self, ctx: Context, ev: NewTaskCreated
    ) -> PromptGenerated:
        task = await ctx.get("task")
        system_prompt = get_system_prompt(self.mode, task)
        return PromptGenerated(prompt=system_prompt, is_system_prompt=True)

    @step
    async def prompt_llm(self, ctx: Context, ev: PromptGenerated) -> LLMResponded:
        prompt = ev.prompt
        if self.verbose_prompt:
            print(prompt)
        if ev.is_system_prompt:
            self.chat_history.append(ChatMessage(role="system", content=prompt))
        else:
            self.chat_history.append(
                ChatMessage(
                    role="user",
                    content=prompt
                    + get_environment_reminder_prompt(await ctx.get("task")),
                )
            )
        response = await self.llm.achat(messages=self.chat_history)
        self.chat_history.append(response.message)
        return LLMResponded(response=str(response))

    @step
    async def handle_response(
        self, ev: LLMResponded
    ) -> ToolCallRequired | PromptGenerated:
        response = ev.response
        pattern = r"<(?P<tag>(?!thinking\b)\w+)[^>]*>.*</(?P=tag)>"
        match = re.search(pattern, response, re.DOTALL)
        if not match:
            return PromptGenerated(
                prompt="You did not use any tool, please use appropriate tool using valid tool format."
            )
        clean_response = re.sub(
            r"<(?P<tag>(?!thinking\b)\w+)[^>]*>.*?</(?P=tag)>",
            "",
            response,
            flags=re.DOTALL,
        ).strip()
        clean_response = re.sub(
            r"</thinking>", "\n" + "-" * 80 + "\n", clean_response
        ).strip()
        clean_response = re.sub(
            r"```xml.*?```", "", clean_response, flags=re.DOTALL
        ).strip()
        clean_response = re.sub(r"^\s*(assistant:\s*)+", "", clean_response).strip()
        clean_response = re.sub(
            r"<thinking>", "\n# Thought process" + "-" * 63 + "\n", clean_response
        )
        if self.verbose_prompt:
            print(f"\n{response}\n")
        else:
            if clean_response.strip():
                print(f"\n🐯 {ANSI_GREEN}Tig:{ANSI_RESET} {clean_response}\n")
        tool = parse_tool_call(response.strip())
        if not tool:
            return PromptGenerated(
                prompt="You did not use any tool, please use appropriate tool using valid tool format."
            )
        return ToolCallRequired(tool=tool)

    @step
    async def use_tool(self, ev: ToolCallRequired) -> PromptGenerated | StopEvent:
        tool_name = list(ev.tool.keys())[0]
        tool_arguments = ev.tool[tool_name]
        print(f"\n🛠️ Using tool: {tool_name}\n")
        try:
            if tool_name == "list_files":
                return PromptGenerated(prompt=list_files(tool_arguments))
            elif tool_name == "ask_followup_question":
                return PromptGenerated(
                    prompt=ask_followup_questions(tool_arguments),
                )
            elif tool_name == "read_file":
                return PromptGenerated(
                    prompt=read_file(tool_arguments, self.auto_approve),
                )
            elif tool_name == "list_code_definition_names":
                return PromptGenerated(
                    prompt=list_code_definitions(tool_arguments, self.auto_approve),
                )
            elif tool_name == "search_files":
                return PromptGenerated(
                    prompt=regex_search_files(tool_arguments, self.auto_approve),
                )
            elif tool_name == "write_to_file":
                return PromptGenerated(
                    prompt=write_to_file(tool_arguments, self.mode, self.auto_approve),
                )
            elif tool_name == "apply_diff":
                return PromptGenerated(
                    prompt=apply_diff(tool_arguments, self.mode, self.auto_approve),
                )
            elif tool_name == "execute_command":
                return PromptGenerated(
                    prompt=execute_command(tool_arguments),
                )
            elif tool_name == "attempt_completion":
                if "result" in tool_arguments:
                    print(f"\n{tool_arguments['result']}\n")
                return StopEvent(message="Task completed successfully.")
            else:
                return PromptGenerated(
                    prompt=f"Tool {tool_name} is not a valid tool. Please use a valid tool."
                )
        except Exception as e:
            return PromptGenerated(
                prompt=f'Error occurred while using tool "{tool_name}": {str(e)}\nMake sure to use tools correctly in valid tool format and valid arguments.'
            )
