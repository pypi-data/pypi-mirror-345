"""
Modality output classes for modality-based model classification
"""
from http import HTTPStatus
from typing import Optional, Any, List

from aixplain.model_interfaces.schemas.api.basic_api_output import APIOutput

class TextOutput(APIOutput):
    """The standardized schema of the aiXplain's text API outputs.

    :param data:
        Output data from the model.
    :type data:
        str
    """
    data: str

class TextListOutput(APIOutput):
    """The standardized schema of the aiXplain's text list API utputs.

    :param data:
        Output data from the model.
    :type data:
        List[str]
    """
    data: List[str]