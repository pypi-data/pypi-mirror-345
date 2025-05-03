from pydantic import BaseModel
from typing import Any, Optional, List, Dict, Union
import tornado.web
from http import HTTPStatus

from aixplain.model_interfaces.schemas.metric.metric_input import MetricAggregate

class MetricOutput(BaseModel):
    """The standardized schema of the aiXplain's Metric API Output.

    :param data:
        Processed output data from supplier metric.
    :type data:
        Any
    :param details:
        Details of the output data. Optional.
    :type details:
        List[str] or Dict[str, str]
    :param metric_aggregate:
        Metadata to be sent as input to the aggregation function. Optional.
    :type metric_aggregate:
        MetricAggregate
    """

    data: Any
    details: Optional[Union[List[str], Dict[str, str]]] = []
    metric_aggregate: Optional[MetricAggregate] = None


class TextGenerationMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """

    data: Any
    details: Optional[Union[List[Any], Dict[str, Any]]] = {}
    metric_aggregate: Optional[MetricAggregate] = None


class TextGenerationMetricOutput(TextGenerationMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError:
            raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason="Incorrect types passed into TextGenerationMetricOutput")


class ReferencelessTextGenerationMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """

    data: Any
    details: Optional[Union[List[str], Dict[str, Any]]] = {}


class ReferencelessTextGenerationMetricOutput(TextGenerationMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError as e:
            raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason=f"{e}  Incorrect types passed into ReferencelessTextGenerationMetricOutput")


class AudioGenerationMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """

    data: Any
    details: Optional[Union[List[Any], Dict[str, Any]]] = {}
    metric_aggregate: Optional[MetricAggregate] = None


class AudioGenerationMetricOutput(AudioGenerationMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError:
            raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason="Incorrect types passed into AudioGenerationMetricOutput")


class ReferencelessAudioGenerationMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """

    data: Any
    details: Optional[Union[List[str], Dict[str, Any]]] = {}


class ReferencelessAudioGenerationMetricOutput(AudioGenerationMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError:
            raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason="Incorrect types passed into ReferencelessAudioGenerationMetricOutput")


class ClassificationMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """

    data: Any
    details: Optional[Union[List[str], Dict[str, Any]]] = {}


class ClassificationMetricOutput(ClassificationMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError:
            raise tornado.web.HTTPError(status_code=HTTPStatus.BAD_REQUEST, reason="Incorrect types passed into ClassificationMetricOutput")

class NamedEntityRecognitionMetricOutputSchema(MetricOutput):
    """The standardized schema of the aiXplain's Metric Output.
    :param data:
        Processed output data from metric.
    :type data:
        Any
    :param details:
        Details of the metric.
    :type details:
        Optional[Union[List[str], Dict[str, str]]]
    """ 
    data: Any
    details: Optional[Union[List[str], Dict[str, Any]]] = {}


class NamedEntityRecognitionMetricOutput(NamedEntityRecognitionMetricOutputSchema):
    def __init__(self, **input):
        try:
            super().__init__(**input)
        except ValueError:
            raise tornado.web.HTTPError(
                status_code=HTTPStatus.BAD_REQUEST,
                reason="Incorrect types passed into NamedEntityRecognitionMetricOutput"
            )
