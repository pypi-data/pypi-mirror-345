"""Connectors dependencies for the dashboard."""

from .duck_db import DuckDBConnectorDependency
from .http import HttpConnectorDependency
from .snowflake import SnowflakeConnectorDependency

__all__ = [
    "HttpConnectorDependency",
    "DuckDBConnectorDependency",
    "SnowflakeConnectorDependency",
]
