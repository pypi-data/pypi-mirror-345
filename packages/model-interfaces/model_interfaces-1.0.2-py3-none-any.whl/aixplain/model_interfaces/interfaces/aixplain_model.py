from kserve.model import Model
from typing import Dict, List
from abc import abstractmethod

from aixplain.model_interfaces.schemas.function.function_input import APIInput
from aixplain.model_interfaces.schemas.function.function_output import APIOutput

class AixplainModel(Model):

    @abstractmethod
    def run_model(self, api_input: Dict[str, List[APIInput]], headers: Dict[str, str] = None) -> Dict[str, List[APIOutput]]:
        pass

    @abstractmethod
    def predict(self, request: Dict[str, List[APIInput]], headers: Dict[str, str] = None) -> Dict[str, List[APIOutput]]:
        pass