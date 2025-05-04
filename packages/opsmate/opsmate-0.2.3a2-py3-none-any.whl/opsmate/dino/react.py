from typing import (
    List,
    Union,
    Callable,
    Coroutine,
    Any,
    ParamSpec,
    TypeVar,
    Awaitable,
    Dict,
)
from pydantic import BaseModel
from .dino import dino
from .types import Message, React, ReactAnswer, Observation, ToolCall, Context
from opsmate.libs.core.trace import traceit
from opentelemetry import trace
from opsmate.runtime.runtime import Runtime
from functools import wraps
import inspect
import structlog
import yaml

logger = structlog.get_logger(__name__)
tracer = trace.get_tracer("opsmate.dino")


async def _react_prompt(
    question: str, message_history: List[Message] = [], tool_names: List[BaseModel] = []
):
    """
    <assistant>
    You run in a loop of question, thought, action.
    At the end of the loop you output an answer.
    Use "Question" to describe the question you have been asked.
    Use "Thought" to describe your thought
    Use "Action" to describe the action you are going to take based on the thought.
    Use "Answer" as the final answer to the question.
    </assistant>

    <response format 1>
    During the thought phase you response with the following format:
    thought: ...
    action: ...
    </response_format 1>

    <response format 2>
    When you have an answer, you response with the following format:
    answer: ...
    </response_format 2>

    <important 1>
    If you are requested with a general query in which you can answer outright without accessing to any internal knowledge-base,
    you can directly give the answer without going through the thought process.

    These query often include:
    - How can I install a curl package?
    - Can you provide me with instructions on how to install a curl package?
    - What are the steps to install a curl package?

    And does not include:
    - How can I install $A_INTERNAL_TOOL where you have no knowledge of $A_INTERNAL_TOOL
    - Can you provide me with instructions on how to install $A_INTERNAL_TOOL
    - What are the steps to install $A_INTERNAL_TOOL

    For example:

    User: how to kill process with pid 1234?

    GOOD Response:
    <answer>
    You can kill process with pid 1234 using the `kill -TERM 1234` command.
    </answer>

    BAD Response:
    <react>
    thought: I need to kill process using the kill command
    action: run `kill -TERM 1234`
    </react>
    </important 1>

    <important 2>
    When you are asked how to perform a task, provide the steps as an action rather than giving them as an answer.

    BAD EXAMPLE:
    <react>
    answer: to kill process with pid 1234, use `kill -TERM 1234`
    </react>

    GOOD EXAMPLE:

    <react>
    thought: I need to kill process using the kill command
    action: run `kill -TERM 1234`
    </react>
    </important 2>

    <important 3>
    Action must be atomic.

    Good: find all the processes that use 100%+ CPU
    Bad: find all the processes that use 100%+ CPU and kill them
    </important 3>
    """

    return [
        Message.system(
            f"""
Here is a list of tools you can use:
{"\n".join(f"<tool>\n{t.__name__}: \n{t.__doc__}\n</tool>" for t in tool_names)}
""",
        ),
        Message.user(question),
        *message_history,
    ]


@traceit(
    exclude=[
        "contexts",
        "tools",
        "chat_history",
        "react_prompt",
        "tool_call_context",
        "thinking",
    ]
)
async def run_react(
    question: str,
    contexts: List[str | Message] = [],
    model: str = "gpt-4o",
    tools: List[ToolCall] = [],
    chat_history: List[Message] = [],
    max_iter: int = 10,
    react_prompt: Callable[
        [str, List[Message], List[ToolCall]], Coroutine[Any, Any, List[Message]]
    ] = _react_prompt,
    tool_calls_per_action: int = 3,
    tool_call_context: Dict[str, Any] = {},
    span: trace.Span = None,
    **kwargs: Any,
):
    ctxs = []
    for ctx in contexts:
        if isinstance(ctx, str):
            ctxs.append(
                Message.system(ctx)
            )  # by this point, ctxs contains the system prompt
        elif isinstance(ctx, Message):
            ctxs.append(ctx)
        else:
            raise ValueError(f"Invalid context type: {type(ctx)}")

    tool_call_model = kwargs.get("tool_call_model", model)

    @dino(tool_call_model, response_model=Observation, tools=tools, **kwargs)
    async def run_action(react: React, context: Dict[str, Any] = {}):
        f"""
        You are a world class expert to carry out actions using the tools you are given.
        Please stictly only carry out the action within the <action>...</action> tag.
        """
        return [
            # *ctxs,
            *message_history,
            Message.assistant(
                f"""
<question-from-user>
{question}
</question-from-user>

<context>
thought: {react.thoughts}
</context>

<important>
* The tool you use must be relevant to the action.
* Please use no more than {tool_calls_per_action} tool calls at a time.
</important>
            """,
            ),
            Message.user(
                f"""<action>
{react.action}
</action>"""
            ),
        ]

    react = dino(model, response_model=Union[React, ReactAnswer], **kwargs)(
        react_prompt
    )

    message_history = Message.normalise(chat_history)
    for ctx in ctxs:
        message_history.append(ctx)
    for i in range(max_iter):
        with tracer.start_as_current_span(f"dino.react.iter.{i}") as iter_span:
            react_result = await react(
                question, message_history=message_history, tool_names=tools
            )
            if isinstance(react_result, React):
                iter_span.add_event(
                    "dino.react.thinking",
                    attributes={
                        "dino.react.type": "thinking",
                        "dino.react.thoughts": react_result.thoughts,
                        "dino.react.action": react_result.action,
                    },
                )
                iter_span.set_attributes(
                    {
                        "dino.react.type": "thinking",
                        "dino.react.thoughts": react_result.thoughts,
                        "dino.react.action": react_result.action,
                    }
                )
                message_history.append(Message.user(react_result.model_dump_json()))
                yield react_result
                with tracer.start_as_current_span(
                    "dino.react.action",
                    attributes={
                        "dino.react.type": "action",
                        "dino.react.action": react_result.action,
                    },
                ) as action_span:
                    observation = await run_action(
                        react_result, context=tool_call_context
                    )
                    action_span.set_attribute(
                        "dino.react.observation",
                        observation.observation,
                    )

                    observation_out = observation.model_dump()
                    for idx, tool_output in enumerate(observation.tool_outputs):
                        if isinstance(tool_output, ToolCall):
                            observation_out["tool_outputs"][
                                idx
                            ] = tool_output.prompt_display()
                        elif isinstance(tool_output, str):
                            observation_out["tool_outputs"][idx] = tool_output

                    action_span.set_attribute(
                        "dino.react.observation.tool_outputs",
                        observation_out["tool_outputs"],
                    )
                    action_span.add_event(
                        "dino.react.observation",
                        attributes={
                            "dino.react.observation": observation.observation,
                            "dino.react.observation.tool_outputs": observation_out[
                                "tool_outputs"
                            ],
                        },
                    )
                    message_history.append(Message.user(yaml.dump(observation_out)))
                    yield observation
            elif isinstance(react_result, ReactAnswer):
                iter_span.set_attributes(
                    {
                        "dino.react.type": "answer",
                        "dino.react.answer": react_result.answer,
                    }
                )
                yield react_result
                break


def react(
    model: str,
    tools: List[ToolCall] = [],
    contexts: List[str | Context] = [],
    max_iter: int = 10,
    iterable: bool = False,
    callback: Callable[[React | ReactAnswer | Observation], None] = None,
    tool_calls_per_action: int = 3,
    **react_kwargs: Any,
):
    """
    Decorator to run a function in a loop of question, thought, action.

    Example:

    ```
    @react(model="gpt-4o", tools=[knowledge_query], context="you are a domain knowledge expert")
    async def knowledge_agent(query: str):
        return f"answer the query: {query}"
    ```
    """

    P = ParamSpec("P")
    T = TypeVar("T")

    async def _extend_contexts(
        contexts: List[str | Context], runtimes: Dict[str, Runtime] | None = None
    ):
        for ctx in contexts:
            if isinstance(ctx, str):
                yield Message.system(ctx)
            elif isinstance(ctx, Context):
                for c in await ctx.resolve_contexts(runtimes=runtimes):
                    yield c
            else:
                raise ValueError(f"Invalid context type: {type(ctx)}")

    def _extend_tools(contexts: List[str | Context]):
        for ctx in contexts:
            if isinstance(ctx, Context):
                for tool in ctx.resolve_tools():
                    yield tool

    def wrapper(fn: Callable[P, Awaitable[T]]):

        _tools = set(tools)
        for tool in _extend_tools(contexts):
            _tools.add(tool)

        _model = model
        _tool_calls_per_action = tool_calls_per_action

        @wraps(fn)
        async def wrapper(
            *args: P.args,
            model: str = None,
            extra_contexts: List[str | Context] = [],
            extra_tools: List[ToolCall] = [],
            tool_calls_per_action: int = _tool_calls_per_action,
            tool_call_context: Dict[str, Any] = {},
            runtimes: Dict[str, Runtime] | None = None,
            **kwargs: P.kwargs,
        ) -> Awaitable[React | Observation | ReactAnswer]:
            ctxs = []
            async for ctx in _extend_contexts(contexts, runtimes=runtimes):
                ctxs.append(ctx)

            if inspect.iscoroutinefunction(fn):
                prompt = await fn(*args, **kwargs)
            else:
                prompt = fn(*args, **kwargs)
            chat_history = kwargs.get("chat_history", [])

            async for ctx in _extend_contexts(extra_contexts, runtimes=runtimes):
                ctxs.append(ctx)

            for tool in _extend_tools(extra_contexts):
                _tools.add(tool)

            for tool in extra_tools:
                _tools.add(tool)

            model = model or _model
            logger.debug("react model", model=model)

            if iterable:

                def gen():
                    return run_react(
                        prompt,
                        model=model,
                        contexts=ctxs,
                        tools=list(_tools),
                        max_iter=max_iter,
                        tool_calls_per_action=tool_calls_per_action,
                        chat_history=chat_history,
                        tool_call_context=tool_call_context,
                        **react_kwargs,
                    )

                return gen()
            else:
                async for result in run_react(
                    prompt,
                    model=model,
                    contexts=ctxs,
                    tools=list(_tools),
                    max_iter=max_iter,
                    tool_calls_per_action=tool_calls_per_action,
                    chat_history=chat_history,
                    tool_call_context=tool_call_context,
                    **react_kwargs,
                ):
                    if callback:
                        if inspect.iscoroutinefunction(callback):
                            await callback(result)
                        else:
                            callback(result)
                    if isinstance(result, ReactAnswer):
                        return result

        return wrapper

    return wrapper
