__author__ = "aiXplain"

from http import HTTPStatus
from typing import Dict, List
import tornado.web
from fastapi.responses import JSONResponse

from aixplain.model_interfaces.schemas.metric.metric_input import (
    TextGenerationMetricInput,
    ReferencelessTextGenerationMetricInput,
    ClassificationMetricInput,
    AudioGenerationMetricInput,
    ReferencelessAudioGenerationMetricInput,
    NamedEntityRecognitionMetricInput,
    MetricAggregate,
)
from aixplain.model_interfaces.schemas.metric.metric_output import (
    TextGenerationMetricOutput,
    ReferencelessTextGenerationMetricOutput,
    ClassificationMetricOutput,
    AudioGenerationMetricOutput,
    ReferencelessAudioGenerationMetricOutput,
    NamedEntityRecognitionMetricOutput,
)

from aixplain.model_interfaces.interfaces.aixplain_metric import AixplainMetric


class TextGenerationMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run_metric(
        self,
        api_input: Dict[str, List[TextGenerationMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[TextGenerationMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request['instances']):
            request["instances"][i] = TextGenerationMetricInput(**instance)

        # Run metric
        outputs = self.run_metric(request, headers=headers)

        # Convert MetricOutput into JSON serializables
        for i, instance in enumerate(outputs["scores"]):
            TextGenerationMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs


class ReferencelessTextGenerationMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)
        
    def run_metric(
        self,
        api_input: Dict[str, List[ReferencelessTextGenerationMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[ReferencelessTextGenerationMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request['instances']):
            # Validated here instead of the validation layer because the
            # Pydantic settings accomodates for additional params
            # if strict checking is not set to true.
            # We want to block references being passed in referenceless
            # and be flexible to accomodate any other param as a part of
            # future compatibility
            if "references" in instance:
                raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason="The parameter 'references' should not be passed")
            request['instances'][i] = ReferencelessTextGenerationMetricInput(**instance)

        # Run metric
        outputs = self.run_metric(request, headers=headers)

        # Convert MetricOutput into JSON serializables
        for i, instance in enumerate(outputs['scores']):
            ReferencelessTextGenerationMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs
        

class ClassificationMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run_metric(
        self,
        api_input: Dict[str, List[ClassificationMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[ClassificationMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request["instances"]):
            request["instances"][i] = ClassificationMetricInput(**instance)

        # Run metric
        outputs = self.run_metric(request, headers=headers)

        # Convert MetricOutput into JSON serializables
        for i, instance in enumerate(outputs["scores"]):
            ClassificationMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs


class AudioGenerationMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run_metric(
        self,
        api_input: Dict[str, List[AudioGenerationMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[AudioGenerationMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(
        self,
        request: Dict,
        headers: Dict[str, str] = None
    ) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request["instances"]):
            request["instances"][i] = AudioGenerationMetricInput(**instance)

        # Run metric
        outputs = self.run_metric(request, headers=headers)

        # Convert MetricOutput into JSON serializables
        for i, instance in enumerate(outputs["scores"]):
            AudioGenerationMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs


class ReferencelessAudioGenerationMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run_metric(
        self,
        api_input: Dict[str, List[ReferencelessAudioGenerationMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[ReferencelessAudioGenerationMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request["instances"]):
            # Validated here instead of the validation layer because the
            # Pydantic settings accomodates for additional params
            # if strict checking is not set to true.
            # We want to block references being passed in referenceless
            # and be flexible to accomodate any other param as a part of
            # future compatibility
            if "references" in instance:
                return JSONResponse(
                    status_code=HTTPStatus.BAD_REQUEST,
                    content={"error": "The parameter 'references' should not be passed"}
                )
            request["instances"][i] = ReferencelessAudioGenerationMetricInput(**instance)

        outputs = self.run_metric(request, headers=headers)

        for i, instance in enumerate(outputs["scores"]):
            ReferencelessAudioGenerationMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs


class NamedEntityRecognitionMetric(AixplainMetric):
    def __init__(self, name, *args, **kwargs):
        super().__init__(name, *args, **kwargs)

    def run_metric(
        self,
        api_input: Dict[str, List[NamedEntityRecognitionMetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[NamedEntityRecognitionMetricOutput]]:
        return super().run_metric(api_input, headers=headers)

    def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricInput
        for i, instance in enumerate(request["instances"]):
            request["instances"][i] = NamedEntityRecognitionMetricInput(**instance)

        # Run metric
        outputs = self.run_metric(request, headers=headers)

        # Convert MetricOutput into JSON serializables
        for i, instance in enumerate(outputs["scores"]):
            NamedEntityRecognitionMetricOutput(**instance.dict())
            outputs["scores"][i] = instance.dict()
        return outputs
