"""
Basic class for API outputs
"""
from pydantic import BaseModel
from typing import Any, Optional, Union, List, Dict

class APIOutput(BaseModel):
    """The standardized schema of the aiXplain's API Output.

    :param data:
        Processed output data from supplier model.
    :type data:
        Any
    :param details:
        Details of the output data. Optional.
    :type details:
        List[str] or Dict[str, str]
    """
    data: Any
    details: Optional[Union[List[str], Dict[str, str]]] = []