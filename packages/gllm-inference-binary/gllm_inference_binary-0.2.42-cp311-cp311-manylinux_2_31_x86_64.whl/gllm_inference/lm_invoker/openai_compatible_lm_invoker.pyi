from gllm_inference.lm_invoker.langchain_lm_invoker import LangChainLMInvoker as LangChainLMInvoker
from typing import Any

class OpenAICompatibleLMInvoker(LangChainLMInvoker):
    """A language model invoker to interact with language models via endpoints compatible with OpenAI API contracts.

    The OpenAICompatibleLMInvoker class is a subclass of LangChainLMInvoker that is specifically designed to interact
    with language models via endpoints that are compatible with the OpenAI API contracts.
    It is built on top of the LangChain library and utilizes the ChatOpenAI class to interact with the language model.

    Attributes:
        llm (ChatOpenAI): The LLM instance to interact with a language model hosted in a specific url.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Tool]): The list of tools provided to the language model to enable tool calling.
        has_structured_output (bool): Whether the model is instructed to produce output with a certain schema.
    """
    def __init__(self, base_url: str, model_name: str, api_key: str | None = None, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, bind_tools_params: dict[str, Any] | None = None, with_structured_output_params: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the OpenAICompatibleLMInvoker class.

        Args:
            base_url (str): The base URL for LLM API.
            model_name (str): The name of the model.
            api_key (str | None, optional): The API key for authentication. Defaults to None.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            bind_tools_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's `bind_tool()`
                method. Used to add tool calling capability to the language model. If provided, must at least include
                the `tools` key. Defaults to None.
            with_structured_output_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's
                `with_structured_output` method. Used to instruct the model to produce output with a certain schema.
                If provided, must at least include the `schema` key. Defaults to None.

        For more details regarding the `bind_tools_params` and `with_structured_output_params`, please refer to
        https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html
        """
