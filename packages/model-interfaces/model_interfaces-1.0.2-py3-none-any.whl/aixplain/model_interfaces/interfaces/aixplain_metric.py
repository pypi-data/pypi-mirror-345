__author__='aiXplain'

from abc import abstractmethod
from enum import Enum
import inspect
import json
import logging
import time
from typing import Dict, List

from aixplain.model_interfaces.schemas.metric.metric_input import MetricInput, MetricAggregate
from aixplain.model_interfaces.schemas.metric.metric_output import MetricOutput

class MetricType(Enum):
    SCORE = 1
    AGGREGATE = 2

def get_latency_ms(start: float, end: float) -> float:
    return round((end - start) * 1000, 9)

class AixplainMetric():
    def __init__(self, name, *args, **kwargs):
        self.name = name
        self.ready = False
        self.enable_latency_logging = False

    async def __call__(self, body: Dict,
                       metric_type: MetricType = MetricType.SCORE,
                       headers: Dict[str, str] = None) -> Dict:
        """Method to call scoring or aggregation with the given input.
        :param body:
            Request payload body.
        :type body:
            Dict
        :param metric_type:
            Metric type enum. Can be either scoring or aggregation.
        :type metric_type:
            MetricType
        :param headers:
            Request headers.
        :type headers:
            Dict
        :return:
            Response output from Metric endpoint function - score or aggregate
        :rtype:
            Dict
        """
        request_id = headers.get("x-request-id", "N.A.") if headers else "N.A."

        # latency vars
        aggregate_ms = 0
        score_ms = 0

        body = json.loads(body) #TODO(krishnadurai): Check if this is the best place for JSON conversion
        if metric_type == MetricType.AGGREGATE:
            start = time.time()
            response = (await self.aggregate(body, headers)) if inspect.iscoroutinefunction(self.aggregate) \
                else self.aggregate(body, headers)
            aggregate_ms = get_latency_ms(start, time.time())
        elif metric_type == MetricType.SCORE:
            start = time.time()
            response = (await self.score(body, headers)) if inspect.iscoroutinefunction(self.score) \
                else self.score(body, headers)
            score_ms = get_latency_ms(start, time.time())
        else:
            raise NotImplementedError()

        if self.enable_latency_logging is True:
            logging.info(f"requestId: {request_id},"
                         f"score_ms: {score_ms}, aggregate_ms: {aggregate_ms}, ")

        return response

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

    @abstractmethod
    def run_aggregation(
        self,
        request: Dict[str, List[List[MetricAggregate]]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[MetricAggregate]]:
        """
        Combines MetricAggregates to form a combined MetricAggregate object.
        """
        pass

    @abstractmethod
    def run_metric(
        self,
        api_input: Dict[str, List[MetricInput]],
        headers: Dict[str, str] = None
    ) -> Dict[str, List[MetricOutput]]:
        pass

    @abstractmethod
    async def score(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        pass
    
    async def aggregate(self, request: Dict, headers: Dict[str, str] = None) -> Dict[str, List]:
        # Convert JSON serializables into MetricAggregate
        for i, scores in enumerate(request["instances"]):
            request["instances"][i] = [MetricAggregate(**score) for score in scores]

        # Aggregate Scores
        outputs = self.run_aggregation(request)

        # Convert MetricAggregate into JSON serializables
        for i, instance in enumerate(outputs["aggregates"]):
            outputs["aggregates"][i] = instance.dict()
        return outputs
