import asyncio
import os
import pkg_resources
import socket
from typing import List

# This is related to how multiprocessing is implemeneted on MacOS
USE_MULTIPROCESS_ENV_NAME = "USE_MULTIPROCESS_PACKAGE"
USE_MULTIPROCESS = os.getenv(USE_MULTIPROCESS_ENV_NAME, default=False)
if USE_MULTIPROCESS:
    import multiprocess as mp
else:
    import multiprocessing as mp

import uvicorn
from fastapi import FastAPI, Request, Response
from fastapi.routing import APIRoute as FastAPIRoute
from fastapi.responses import ORJSONResponse
from prometheus_client import REGISTRY, exposition
from timing_asgi import TimingMiddleware, TimingClient
from timing_asgi.integrations import StarletteScopeToName
import logging

from aixplain.model_interfaces.interfaces.metric_server.dataplane import DataPlane
from aixplain.model_interfaces.interfaces.metric_server.metric_errors import (
    InvalidInput, MetricNotFound, MetricNotReady, invalid_input_handler,
    metric_not_found_handler, metric_not_ready_handler, not_implemented_error_handler,
    generic_exception_handler
)
from aixplain.model_interfaces.interfaces.metric_server.v1_endpoints import V1Endpoints


DATE_FMT = "%Y-%m-%d %H:%M:%S"


async def metrics_handler(request: Request) -> Response:
    encoder, content_type = exposition.choose_encoder(request.headers.get("accept"))
    return Response(content=encoder(REGISTRY), headers={"content-type": content_type})


class PrintTimings(TimingClient):
    def timing(self, metric_name, timing, tags):
        logging.info(f"{metric_name} {timing}, {tags}")


class RESTServer:
    def __init__(self, data_plane: DataPlane, enable_docs_url=False):
        self.dataplane = data_plane
        self.enable_docs_url = enable_docs_url

    def create_application(self) -> FastAPI:
        """Create a Aixplain Metric Server application with API routes.
        Returns:
            FastAPI: An application instance.
        """
        v1_endpoints = V1Endpoints(self.dataplane)

        return FastAPI(
            title="Aixplain Metric Server",
            version=pkg_resources.get_distribution("model_interfaces").version,
            docs_url="/docs" if self.enable_docs_url else None,
            redoc_url=None,
            default_response_class=ORJSONResponse,
            routes=[
                # Server Liveness API returns 200 if server is alive.
                FastAPIRoute(r"/", v1_endpoints.live),
                # Model Health API returns 200 if model is ready to serve.
                ### (TODO) krishnadurai: Metric is not sent to v1_endpoints. Solve!
                FastAPIRoute(r"/v1/metrics/{metric_name}", v1_endpoints.metric_ready, tags=["V1"]),
                FastAPIRoute(r"/v1/metrics/{metric_name}:score",
                             v1_endpoints.score, methods=["POST"], tags=["V1"]),
                FastAPIRoute(r"/v1/metrics/{metric_name}:aggregate",
                             v1_endpoints.aggregate, methods=["POST"], tags=["V1"]),
                FastAPIRoute(r"/v1/health/live",
                             v1_endpoints.live, methods=["GET"], tags=["V1"]),
                FastAPIRoute(r"/v1/health/ready",
                             v1_endpoints.ready, methods=["GET"], tags=["V1"]),
            ], exception_handlers={
                InvalidInput: invalid_input_handler,
                MetricNotFound: metric_not_found_handler,
                MetricNotReady: metric_not_ready_handler,
                NotImplementedError: not_implemented_error_handler,
                Exception: generic_exception_handler
            }
        )

class UvicornProcess(mp.Process):

    def __init__(self, http_port: int, sockets: List[socket.socket],
                 data_plane: DataPlane, enable_docs_url):
        super().__init__()
        self.sockets = sockets
        self.server = RESTServer(data_plane, enable_docs_url)
        app = self.server.create_application()
        app.add_middleware(
            TimingMiddleware,
            client=PrintTimings(),
            metric_namer=StarletteScopeToName(prefix="aixplain.com", starlette_app=app)
        )
        self.cfg = uvicorn.Config(
            app=app,
            host="0.0.0.0",
            port=http_port,
            log_config={
                "version": 1,
                "formatters": {
                    "default": {
                        "()": "uvicorn.logging.DefaultFormatter",
                        "datefmt": DATE_FMT,
                        "fmt": "%(asctime)s.%(msecs)03d %(name)s %(levelprefix)s %(message)s",
                        "use_colors": None,
                    },
                    "access": {
                        "()": "uvicorn.logging.AccessFormatter",
                        "datefmt": DATE_FMT,
                        "fmt": '%(asctime)s.%(msecs)03d %(name)s %(levelprefix)s %(client_addr)s %(process)s - '
                               '"%(request_line)s" %(status_code)s',
                        # noqa: E501
                    },
                },
                "rest": {
                    "default": {
                        "formatter": "default",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stderr",
                    },
                    "access": {
                        "formatter": "access",
                        "class": "logging.StreamHandler",
                        "stream": "ext://sys.stdout",
                    },
                },
                "loggers": {
                    "uvicorn": {"rest": ["default"], "level": "INFO"},
                    "uvicorn.error": {"level": "INFO"},
                    "uvicorn.access": {"rest": ["access"], "level": "INFO", "propagate": False},
                },
            }
        )

    def stop(self):
        self.terminate()

    def run(self):
        server = uvicorn.Server(config=self.cfg)
        asyncio.run(server.serve(sockets=self.sockets))