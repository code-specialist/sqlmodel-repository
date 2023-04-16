import logging
import sys

import structlog
from structlog.processors import JSONRenderer

sqlmodel_repository_logger: structlog.WriteLogger = structlog.get_logger("SQLModelRepositoryLogger")
logging.basicConfig(format="[%(levelname)s] %(asctime)s - %(message)s function='%(funcName)s'", stream=sys.stdout, level=logging.DEBUG)
structlog.configure(
    processors=[
        structlog.contextvars.merge_contextvars,
        JSONRenderer(),
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

__all__ = ["sqlmodel_repository_logger"]
