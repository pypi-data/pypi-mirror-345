"""
Basic class for API inputs
"""
from pydantic import BaseModel
from typing import Any, Optional

class APIInput(BaseModel):
    """The standardized schema of the aiXplain's API input.
    
    :param data:
        Input data to the model.
    :type data:
        Any
    :param supplier:
        Supplier name.
    :type supplier:
        str
    :param function:
        The aixplain function name for the model. 
    :type function:
        str 
    :param version:
        The version number of the model if the supplier has multiple 
        models with the same function. Optional.  
    :type version:
        str
    :param language:
        The language the model processes (if relevant). Optional.
    :type language:
        str
    """
    data: Any
    supplier: Optional[str] = ""
    function: Optional[str] = ""
    version: Optional[str] = ""
    language: Optional[str] = ""