"""Specs for dependencies."""

from .connectors import DuckDBConnectorDependency
from .connectors import HttpConnectorDependency
from .connectors import SnowflakeConnectorDependency
from .datastore import DashboardBlobStorage
from .datastore import DashboardFileShareStorage
from .http import HttpDependency
from .route import RouteDependency
from .widget import WidgetSelectDependency

__all__ = [
    # .datastore
    "DashboardBlobStorage",
    "DashboardFileShareStorage",
    # .widget
    "WidgetSelectDependency",
    # .route
    "RouteDependency",
    # .http
    "HttpDependency",
    # .connectors
    "HttpConnectorDependency",
    "DuckDBConnectorDependency",
    "SnowflakeConnectorDependency",
]
