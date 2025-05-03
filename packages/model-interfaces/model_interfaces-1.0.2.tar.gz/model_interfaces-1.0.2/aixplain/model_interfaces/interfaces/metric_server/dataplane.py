import pkg_resources
from typing import List, Dict, Optional

from aixplain.model_interfaces.interfaces.aixplain_metric import AixplainMetric, MetricType
from aixplain.model_interfaces.interfaces.metric_server.metric_errors import MetricNotFound

class AssetRepository:
    def __init__(self):
        self.assets: Dict[str, AixplainMetric] = {}
    
    def get_asset(self, name: str) -> Optional[AixplainMetric]:
        return self.assets.get(name, None)
    
    def update(self, asset: AixplainMetric):
        self.assets[asset.name] = asset

class DataPlane:
    """Metric DataPlane
    """

    def __init__(self, asset_repository: AssetRepository):
        self._server_name = "aixplain_metric_server"
        self._server_version = pkg_resources.get_distribution("model_interfaces").version
        self._asset_repo = asset_repository

    @staticmethod
    async def live() -> Dict[str, str]:
        """Server live.
        Returns ``{"status": "alive"}`` on successful invocation.
        Primarily meant to be used for Kubernetes liveness check.
        Returns:
            Dict: {"status": "alive"}
        """
        return {"status": "alive"}

    @staticmethod
    async def ready() -> bool:
        """Server ready.
        Returns ``True``. Primarily meant to be used as Kubernetes readiness check.
        Returns:
            bool: True
        """
        return True
    
    def get_metric(self, name: str) -> AixplainMetric:
        model = self._asset_repo.get_asset(name)
        if model is None:
            raise MetricNotFound(name)
        return model

    def is_metric_ready(self, metric_name: str):
        metric = self.get_metric(metric_name)
        if isinstance(metric, AixplainMetric):
            return False if metric is None else metric.ready
        return False

    async def score(
            self,
            metric_name: str,
            body: Dict[str, List],
            headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        metric = self.get_metric(metric_name)

        response = await metric(body, headers=headers, metric_type=MetricType.SCORE)

        response, response_headers = response, {} #TODO(krishnadurai): Check headers to return
        return response, response_headers

    async def aggregate(
            self,
            metric_name: str,
            body: Dict[str, List],
            headers: Optional[Dict[str, str]] = None
    ) -> List[Dict[str, str]]:
        metric = self.get_metric(metric_name)

        response = await metric(body, headers=headers, metric_type=MetricType.AGGREGATE)

        response, response_headers = response, {}
        return response, response_headers
