__author__='aiXplain'

from abc import abstractmethod
from kserve.model import Model
from typing import Dict, List, Any
from pydantic import validate_call

from aixplain.model_interfaces.schemas.script.script_input import ScriptInput
from aixplain.model_interfaces.schemas.script.script_output import ScriptOutput

class ProjectNode(Model):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name)
        self.name = name
        self.ready = False
        ready = self.load()
        print(f"Readiness: {ready}")
        assert ready

    @validate_call
    def predict(self, request: Dict[str, List[ScriptInput]], headers: Dict[str, str] = None) -> Dict[str, List[ScriptOutput]]:
        instances = request["instances"]
        results = []
        for instance in instances:
            result = self.run_script(instance)
            results.append(result)
        predictions =  {
            "predictions": results
        }
        return predictions

    @validate_call
    def run_script(self, input: Any) -> Any:
        raise NotImplementedError

    def load(self) -> bool:
        """Load handler can be overridden to load the metric from storage
        ``self.ready`` flag is used for metric health check
        :return:
            True if metric is ready, False otherwise
        :rtype:
            Bool
        """
        self.ready = True
        return self.ready