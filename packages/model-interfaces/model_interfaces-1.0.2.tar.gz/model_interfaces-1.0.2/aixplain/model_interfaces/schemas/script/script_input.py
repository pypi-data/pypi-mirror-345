__author__ = "aiXplain"

from pydantic import BaseModel
from typing import Dict

class ScriptInput(BaseModel):
    """The standardized schema of the aiXplain's Script API input.

    :param inputs:
        Input values to script.
    """
    inputs: Dict