"""
ZeebeeAI Python Client SDK

This package provides a comprehensive client for interacting with the ZeebeeAI Chat Platform.
"""

from .client import ZeebeeClient
from .exceptions import (
    AuthenticationError,
    RateLimitError,
    AgentException,
    PipelineException,
)
from .agents import AgentController
from .pipelines import PipelineController

__version__ = "0.1.0"
__all__ = [
    "ZeebeeClient",
    "AgentController",
    "PipelineController",
    "AuthenticationError",
    "RateLimitError",
    "AgentException",
    "PipelineException",
]
