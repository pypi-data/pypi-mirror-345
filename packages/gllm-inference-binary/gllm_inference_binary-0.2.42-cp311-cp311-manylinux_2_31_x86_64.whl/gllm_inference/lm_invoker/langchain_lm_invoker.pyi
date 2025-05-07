from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.constants import MESSAGE_TUPLE_LENGTH as MESSAGE_TUPLE_LENGTH
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.schema import LMOutput as LMOutput, MultimodalOutput as MultimodalOutput, ToolCall as ToolCall, ToolResult as ToolResult, UnimodalPrompt as UnimodalPrompt
from langchain_core.language_models import BaseChatModel as BaseChatModel
from pydantic import BaseModel as BaseModel
from typing import Any

class LangChainLMInvoker(BaseLMInvoker):
    """A language model invoker to interact with language models defined using LangChain's BaseChatModel.

    The `LangChainLMInvoker` class is responsible for invoking a language model defined using LangChain's
    BaseChatModel module. It handles both standard and streaming invocation. Streaming mode is enabled if an event
    emitter is provided. It also supports both tool calling and structured output capabilities.

    Attributes:
        llm (BaseChatModel): The LLM instance to interact with a language model defined using LangChain's BaseChatModel.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Tool]): The list of tools provided to the language model to enable tool calling.
        has_structured_output (bool): Whether the model is instructed to produce output with a certain schema.

    Output types:
        The output of the `LangChainLMInvoker` is of type `MultimodalOutput`, which is a type alias that can represent:
        1. `str`: A string of the response if no additional output is needed.
        2. `LMOutput`: A Pydantic model with the following attributes if any additional output is needed:
            2.1. response (str): The response from the language model. Defaults to an empty string.
            2.2. tool_calls (list[ToolCall]): The tool calls provided if the model decides to call any of the
                provided `tools`. Defaults to an empty list.
            2.3. structured_output (BaseModel | None): A Pydantic model of the structured output, provided if the
                model is configured to produce structured output. Defaults to None.
    """
    llm: Incomplete
    has_structured_output: Incomplete
    def __init__(self, llm: BaseChatModel, default_hyperparameters: dict[str, Any] | None = None, bind_tools_params: dict[str, Any] | None = None, with_structured_output_params: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the LangChainLMInvoker class.

        Args:
            llm (BaseChatModel): The LLM instance to interact with a language model defined using LangChain's
                BaseChatModel.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            bind_tools_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's `bind_tool()`
                method. Used to add tool calling capability to the language model. If provided, must at least
                include the `tools` key. Defaults to None.
            with_structured_output_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's
                `with_structured_output` method. Used to instruct the model to produce output with a certain schema.
                If provided, must at least include the `schema` key. Defaults to None.

        For more details regarding the `bind_tools_params` and `with_structured_output_params`, please refer to
        https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html
        """
