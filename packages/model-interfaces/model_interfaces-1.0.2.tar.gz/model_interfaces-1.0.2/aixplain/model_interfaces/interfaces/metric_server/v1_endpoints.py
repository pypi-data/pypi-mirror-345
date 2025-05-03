from typing import Dict, Union
from fastapi import Request, Response

from aixplain.model_interfaces.interfaces.metric_server.dataplane import DataPlane
from aixplain.model_interfaces.interfaces.metric_server.metric_errors import MetricNotReady

class V1Endpoints:
    """AiXplain Metrics V1 Endpoints
    """

    def __init__(self, dataplane: DataPlane):
        self.dataplane = dataplane
    
    async def live(self):
        return await self.dataplane.live()
    
    async def ready(self):
        return await self.dataplane.ready()
    
    async def metric_ready(self, metric_name: str) -> Dict[str, Union[str, bool]]:
        """Check if a given metric is ready.
        Args:
            metric_name (str): AixplainMetric name.
        Returns:
            Dict[str, Union[str, bool]]: Name of the metric and whether it's ready.
        """
        metric_ready = self.dataplane.is_metric_ready(metric_name)

        if not metric_ready:
            raise MetricNotReady(metric_name)

    async def score(self, metric_name: str, request: Request) -> Union[Response, Dict]:
        """Score request handler.
        It sends the request to the dataplane where the metric will process the request body.
        Args:
            metric_name (str): AixplainMetric name.
            metric (AixplainMetric): Metric object of AixplainMetric type.
            request (Request): Raw request object.
        Returns:
            Dict|Response: Model inference response.
        """
        body = await request.body()
        headers = dict(request.headers.items())
        response, response_headers = await self.dataplane.score(metric_name=metric_name, body=body, headers=headers)

        if not isinstance(response, dict):
            return Response(content=response, headers=response_headers)
        return response

    async def aggregate(self, metric_name: str, request: Request) -> Union[Response, Dict]:
        """Aggregate handler.
        Args:
            metric_name (str): AixplainMetric name.
            request (Request): Raw request object.
        Returns:
            Dict: Explainer output.
        """
        body = await request.body()
        headers = dict(request.headers.items())
        response, response_headers = await self.dataplane.aggregate(metric_name=metric_name, body=body, headers=headers)

        if not isinstance(response, dict):
            return Response(content=response, headers=response_headers)
        return response
