from PIL.Image import Image as Image
from _typeshed import Incomplete
from gllm_inference.multimodal_em_invoker.multimodal_em_invoker import BaseMultimodalEMInvoker as BaseMultimodalEMInvoker
from gllm_inference.utils import get_mime_type as get_mime_type, is_local_file_path as is_local_file_path, is_remote_file_path as is_remote_file_path

VALID_EXTENSION_MAP: Incomplete
VALID_EXTENSIONS: Incomplete

class VoyageMultimodalEMInvoker(BaseMultimodalEMInvoker[str | bytes]):
    '''A class to interact with multimodal embedding models hosted through Voyage API endpoints.

    The `VoyageMultimodalEMInvoker` class is responsible for invoking a multimodal embedding model using the
    Voyage API. It uses the multimodal embedding model to transform a content or a list of contents
    into their vector representations.

    Attributes:
        client (Client): The client for the Voyage API.
        model_name (str): The name of the multimodal embedding model to be used.

    Notes:
        The `VoyageMultimodalEMInvoker` currently supports the following contents:
        1. Text, which can be passed as plain strings.
        2. Image, which can be passed as:
            1. Base64 encoded image bytes.
            2. URL pointing to an image.
            3. Local image file path.

        Additionally, the `VoyageMultimodalEMInvoker` also supports embedding a list of contents as a single embedding.
        e.g. a text and an image can be embedded as a single embedding. This can be done by passing the list of
        contents as an element of the input list.

    Examples:
        1. A single text content:
           ```
           invoker.invoke("Hi!")
           ```
           will output:
           ```
           [0.1, 0.2, ...] -> embedding of "Hi!"
           ```
        2. A single image content:
           ```
           invoker.invoke("../image.png")
           ```
           will output:
           ```
           [0.3, 0.4, ...] -> embedding of "../image.png"
           ```
        3. A list of contents, containing a text and an image:
           ```
           invoker.invoke(["Hi!", "../image.png"])
           ```
           will output:
           ```
           [
               [0.1, 0.2, ...], -> embedding of "Hi!"
               [0.3, 0.4, ...], -> embedding of "../image.png"
           ]
           ```
        4. A list of contents, containing a list:
           ```
           invoker.invoke([["Hi!", "../image.png"]])
           ```
           will output:
           ```
           [
               [0.5, 0.6, ...], -> embedding of ["Hi!", "../image.png"]
           ]
           ```
        5. A list of contents, containing a list and a text:
           ```
           invoker.invoke([["Hi!", "../image.png"], "Hello!"])
           ```
           will output:
           ```
           [
               [0.5, 0.6, ...], -> embedding of ["Hi!", "../image.png"]
               [0.7, 0.8, ...], -> embedding of "Hello!"
           ]
           ```
    '''
    client: Incomplete
    model_name: Incomplete
    def __init__(self, model_name: str, api_key: str) -> None:
        """Initializes a new instance of the VoyageMultimodalEMInvoker class.

        Args:
            model_name (str): The name of the multimodal embedding model to be used.
            api_key (str): The API key for the Voyage API.
        """
