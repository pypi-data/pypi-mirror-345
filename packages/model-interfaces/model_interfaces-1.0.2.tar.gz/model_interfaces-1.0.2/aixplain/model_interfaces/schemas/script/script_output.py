__author__ = "aiXplain"

from pydantic import BaseModel
from typing import Dict

class ScriptOutput(BaseModel):
    """The standardized schema of the aiXplain's Script API input.

    :param inputs:
        Input values to script.
    """
    outputs: Dict