"""
Modality input classes for modality-based model classification
"""
from http import HTTPStatus
from typing import Optional, Any, List

from aixplain.model_interfaces.schemas.api.basic_api_input import APIInput

class TextInput(APIInput):
    """The standardized schema of the aiXplain's text API inputs.

    :param data:
        Input data to the model.
    :type data:
        str
    """
    data: str
    
class TextListInput(APIInput):
    """The standardized schema of the aiXplain's text list API inputs.

    :param data:
        Input data to the model.
    :type data:
       List[str]
    """
    data: List[str]