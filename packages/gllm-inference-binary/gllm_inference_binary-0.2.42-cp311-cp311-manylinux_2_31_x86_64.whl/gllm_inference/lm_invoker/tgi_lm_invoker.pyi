from _typeshed import Incomplete
from gllm_core.event import EventEmitter as EventEmitter
from gllm_inference.lm_invoker.lm_invoker import BaseLMInvoker as BaseLMInvoker
from gllm_inference.utils.utils import get_basic_auth_headers as get_basic_auth_headers
from typing import Any

class TGILMInvoker(BaseLMInvoker):
    """A language model invoker to interact with language models hosted in Text Generation Inference (TGI).

    The `TGILMInvoker` class is responsible for invoking a language model hosted in TGI.
    It handles both standard and streaming invocation. Streaming mode is enabled if an event emitter is provided.

    Attributes:
        client (AsyncInferenceClient): The client instance to interact with the TGI service.
        default_hyperparameters (dict[str, Any]): Default hyperparameters for invoking the model.
    """
    client: Incomplete
    def __init__(self, url: str, username: str = '', password: str = '', api_key: str | None = None, default_hyperparameters: dict[str, Any] = None) -> None:
        """Initializes a new instance of the TGILMInvoker class.

        Args:
            url (str): The URL of the TGI service.
            username (str, optional): The username for Basic Authentication. Defaults to an empty string.
            password (str, optional): The password for Basic Authentication. Defaults to an empty string.
            api_key (str | None, optional): The API key for the TGI service. Defaults to None.
            default_hyperparameters (dict[str, Any], optional): Default hyperparameters for invoking the model.
                Defaults to None.
        """
