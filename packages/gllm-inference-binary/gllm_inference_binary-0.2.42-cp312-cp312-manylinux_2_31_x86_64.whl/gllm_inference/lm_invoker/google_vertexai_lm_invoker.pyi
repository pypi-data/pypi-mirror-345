from gllm_inference.lm_invoker.langchain_lm_invoker import LangChainLMInvoker as LangChainLMInvoker
from typing import Any

class GoogleVertexAILMInvoker(LangChainLMInvoker):
    """A language model invoker to interact with language models hosted through Google Vertex AI API endpoints.

    The `GoogleVertexAILMInvoker` class is responsible for invoking a language model using the Google Vertex AI
    API. It handles both standard and streaming invocation. Streaming mode is enabled if an event emitter is provided.
    It also supports both tool calling and structured output capabilities.

    Attributes:
        llm (ChatVertexAI): The LLM instance to interact with a language model hosted through Google
            Vertex AI API endpoints.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
        tools (list[Tool]): The list of tools provided to the language model to enable tool calling.
        has_structured_output (bool): Whether the model is instructed to produce output with a certain schema.

    Notes:
        In order to use the `GoogleVertexAILMInvoker`, a credentials JSON file for a Google Cloud service account with
        the Vertex AI API enabled must be provided. For more information on how to create the credentials file,
        please refer to the following pages:
        1. https://cloud.google.com/docs/authentication/application-default-credentials.
        2. https://developers.google.com/workspace/guides/create-credentials.
    """
    def __init__(self, model_name: str, credentials_path: str, model_kwargs: dict[str, Any] | None = None, default_hyperparameters: dict[str, Any] | None = None, bind_tools_params: dict[str, Any] | None = None, with_structured_output_params: dict[str, Any] | None = None) -> None:
        """Initializes a new instance of the GoogleVertexAILMInvoker class.

        Args:
            model_name (str): The name of the Google Vertex AI model.
            credentials_path (str): The path to the Google Cloud service account credentials JSON file.
            model_kwargs (dict[str, Any] | None, optional): Additional model parameters. Defaults to None.
            default_hyperparameters (dict[str, Any] | None, optional): Default hyperparameters for invoking the model.
                Defaults to None.
            bind_tools_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's `bind_tool()`
                method. Used to add tool calling capability to the language model. If provided, must at least include
                the `tools` key. Defaults to None.
            with_structured_output_params (dict[str, Any] | None, optional): The parameters for BaseChatModel's
                `with_structured_output` method. Used to instruct the model to produce output with a certain schema.
                If provided, must at least include the `schema` key. Defaults to None.

        Notes: As of now, the `GoogleVertexAILMInvoker` does not support customizing the `project_id` due to the
        `ChatVertexAI` class from LangChain not supporting the `project_id` parameter.

        For more details regarding the `bind_tools_params` and `with_structured_output_params`, please refer to
        https://python.langchain.com/api_reference/google_vertexai/chat_models/langchain_google_vertexai.chat_models.ChatVertexAI.html
        """
