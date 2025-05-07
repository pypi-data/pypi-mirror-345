from gllm_inference.em_invoker.langchain_em_invoker import LangChainEMInvoker as LangChainEMInvoker
from typing import Any

class VoyageEMInvoker(LangChainEMInvoker):
    """An embedding model invoker to interact with embedding models hosted through Voyage API endpoints.

    The `VoyageEMInvoker` class is responsible for invoking an embedding model using the Voyage API.
    It uses the embedding model to transform a text or a list of input text into their vector representations.

    Attributes:
        em (VoyageEmbeddings): The embedding model instance to interact with Voyage models.
    """
    def __init__(self, model_name: str, api_key: str, model_kwargs: Any = None) -> None:
        """Initializes a new instance of the VoyageEMInvoker class.

        Args:
            model_name (str): The name of the Voyage model to be used.
            api_key (str): The API key for accessing the Voyage model.
            model_kwargs (Any, optional): Additional keyword arguments to initiate the Voyage model. Defaults to None.
        """
