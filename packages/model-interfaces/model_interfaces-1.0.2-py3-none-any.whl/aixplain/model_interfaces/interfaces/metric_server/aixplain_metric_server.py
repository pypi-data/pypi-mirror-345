import argparse
import asyncio
import concurrent.futures
from distutils.util import strtobool
import os
import logging
import psutil
import socket
import sys
from typing import List


from aixplain.model_interfaces.interfaces.aixplain_metric import AixplainMetric
from aixplain.model_interfaces.interfaces.metric_server.dataplane import DataPlane, AssetRepository
from aixplain.model_interfaces.interfaces.metric_server.rest_server import UvicornProcess


DEFAULT_HTTP_PORT = 8080

parser = argparse.ArgumentParser(add_help=False)
parser.add_argument("--http_port", default=DEFAULT_HTTP_PORT, type=int,
                    help="The HTTP Port listened to by the metric server.")
parser.add_argument("--workers", default=1, type=int,
                    help="The number of workers for multi-processing.")
parser.add_argument("--max_threads", default=4, type=int,
                    help="The number of max processing threads in each worker.")
parser.add_argument('--max_asyncio_workers', default=None, type=int,
                    help='Max number of asyncio workers to spawn')
parser.add_argument("--enable_grpc", default=True, type=lambda x: bool(strtobool(x)),
                    help="Enable gRPC for the metric server")
parser.add_argument("--enable_docs_url", default=False, type=lambda x: bool(strtobool(x)),
                    help="Enable docs url '/docs' to display Swagger UI.")
parser.add_argument("--enable_latency_logging", default=True, type=lambda x: bool(strtobool(x)),
                    help="Output a log per request with latency metrics.")

args, _ = parser.parse_known_args()

FORMAT = '%(asctime)s.%(msecs)03d %(process)s %(name)s %(levelname)s [%(funcName)s():%(lineno)s] %(message)s'
DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
logging.basicConfig(level=logging.INFO, format=FORMAT, datefmt=DATE_FORMAT)



def cpu_count():
    """Get the available CPU count for this system.
    Takes the minimum value from the following locations:
    - Total system cpus available on the host.
    - CPU Affinity (if set)
    - Cgroups limit (if set)
    """
    count = os.cpu_count()

    # Check CPU affinity if available
    try:
        affinity_count = len(psutil.Process().cpu_affinity())
        if affinity_count > 0:
            count = min(count, affinity_count)
    except Exception:
        pass

    # Check cgroups if available
    if sys.platform == "linux":
        try:
            with open("/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_quota_us") as f:
                quota = int(f.read())
            with open("/sys/fs/cgroup/cpu,cpuacct/cpu.cfs_period_us") as f:
                period = int(f.read())
            cgroups_count = int(quota / period)
            if cgroups_count > 0:
                count = min(count, cgroups_count)
        except Exception:
            pass

    return count

class AixplainMetricServer:
    """aiXplain Metric Server
    Args:
        http_port (int): HTTP port. Default: ``8080``.
        workers (int): Number of workers for uvicorn. Default: ``1``.
        max_threads (int): Max number of processing threads. Default: ``4``
        max_asyncio_workers (int): Max number of AsyncIO threads. Default: ``None``
        enable_docs_url (bool): Whether to turn on ``/docs`` Swagger UI. Default: ``False``.
        enable_latency_logging (bool): Whether to log latency metric. Default: ``False``.
    """

    def __init__(self, http_port: int = args.http_port,
                 workers: int = args.workers,
                 max_threads: int = args.max_threads,
                 max_asyncio_workers: int = args.max_asyncio_workers,
                 registered_assets: AssetRepository = AssetRepository(),
                 enable_docs_url: bool = args.enable_docs_url,
                 enable_latency_logging: bool = args.enable_latency_logging):
        self.http_port = http_port
        self.workers = workers
        self.max_threads = max_threads
        self.max_asyncio_workers = max_asyncio_workers
        self.registered_assets = registered_assets
        self.enable_docs_url = enable_docs_url
        self.enable_latency_logging = enable_latency_logging
        self.dataplane = DataPlane(asset_repository=self.registered_assets)
    
    def start(self, metrics: List[AixplainMetric]) -> None:
        if isinstance(metrics, list):
            for metric in metrics:
                if isinstance(metric, AixplainMetric):
                    self.register_metric(metric)
                    # pass whether to log request latency into the metric
                    metric.enable_latency_logging = self.enable_latency_logging
                else:
                    raise RuntimeError("Metric type should be 'AixplainMetric'")
        else:
            raise RuntimeError("Unknown metric collection types")

        if self.max_asyncio_workers is None:
            # formula as suggest in https://bugs.python.org/issue35279
            self.max_asyncio_workers = min(32, cpu_count() + 4)

        logging.info(f"Setting max asyncio worker threads as {self.max_asyncio_workers}")
        asyncio.get_event_loop().set_default_executor(
            concurrent.futures.ThreadPoolExecutor(max_workers=self.max_asyncio_workers))

        async def serve():
            serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            serversocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            serversocket.bind(('0.0.0.0', self.http_port))
            serversocket.listen(5)

            logging.info(f"starting uvicorn with {self.workers} workers")
            for _ in range(self.workers):
                server = UvicornProcess(self.http_port, [serversocket],
                                        self.dataplane, self.enable_docs_url)
                server.start()

        async def servers_task():
            servers = [serve()]
            await asyncio.gather(*servers)

        asyncio.run(servers_task())

    def register_metric(self, metric: AixplainMetric):
        if not metric.name:
            raise Exception(
                "Failed to register metric, metric.name must be provided."
            )
        self.registered_assets.update(metric)
        logging.info("Registering metric: %s", metric.name)
