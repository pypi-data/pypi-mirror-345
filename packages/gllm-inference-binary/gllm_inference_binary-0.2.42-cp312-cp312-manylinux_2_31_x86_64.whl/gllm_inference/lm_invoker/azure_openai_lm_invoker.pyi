from gllm_inference.lm_invoker.langchain_lm_invoker import LangChainLMInvoker as LangChainLMInvoker
from typing import Any

class AzureOpenAILMInvoker(LangChainLMInvoker):
    """A language model invoker to interact with language models hosted through Azure OpenAI API endpoints.

    The `AzureOpenAILMInvoker` class is responsible for invoking a language model using the Azure OpenAI API.
    It handles both standard and streaming invocation. Streaming mode is enabled if an event emitter is provided.
    It also supports both tool calling and structured output capabilities.

    Attributes:
        llm (AzureChatOpenAI): The LLM instance to interact with Azure OpenAI models.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Tool]): The list of tools provided to the language model to enable tool calling.
        has_structured_output (bool): Whether the model is instructed to produce output with a certain schema.
    """
    def __init__(self, model_name: str, api_key: str, azure_deployment: str, azure_endpoint: str, api_version: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, bind_tools_params: dict[str, Any] | None = None, with_structured_output_params: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the AzureOpenAILMInvoker class.

        Args:
            model_name (str): The name of the Azure OpenAI model to be used.
            api_key (str): The API key for accessing the Azure OpenAI model.
            azure_deployment (str): The name of the Azure OpenAI deployment to use.
            azure_endpoint (str): The URL endpoint for the Azure OpenAI service.
            api_version (str): The API version of the Azure OpenAI service.
            model_kwargs (dict[str, Any] | None, optional): Additional keyword arguments to initiate the Azure OpenAI
                model. Defaults to None.
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
