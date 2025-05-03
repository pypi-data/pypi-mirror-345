"""Dashboard version class."""

import re
import sys
import warnings
from dataclasses import dataclass
from datetime import datetime
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union
from typing import cast
from urllib.parse import urlparse

from typing_extensions import Unpack

from engineai.sdk.dashboard import config
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.clients import DashboardAPI
from engineai.sdk.dashboard.dashboard.exceptions import DashboardVersionValueError
from engineai.sdk.dashboard.dashboard.exceptions import (
    MetadataLastAvailableDataTypeError,
)
from engineai.sdk.dashboard.dashboard.page.page import Page
from engineai.sdk.dashboard.dashboard.typings import DashboardContent
from engineai.sdk.internal.url_config import PLATFORM_URL

from ..exceptions import DashboardEmptyContentError


@dataclass
class DashboardVersionResponse:
    """Dashboard version response."""

    url_path: str
    version: str
    active: bool
    dashboard_version_id: str
    app_slug: str
    workspace_slug: str
    dashboard_slug: str


class DashboardVersion(AbstractFactory):
    """Spec for Dashboard version."""

    def __init__(
        self,
        workspace_slug: str,
        app_slug: str,
        dashboard_slug: str,
        content: Optional[Union[List[Page], Page, DashboardContent]] = None,
        title: Optional[str] = None,
        **kwargs: Any,
    ) -> None:
        """Construct DashboardVersion Class.

        Args:
            workspace_slug: workspace slug.
            app_slug: app slug.
            dashboard_slug: dashboard slug.
            content: dashboard content.
        """
        deprecated_args = {
            "slug": "The 'slug' parameter is deprecated.",
            "version": "The 'version' parameter is deprecated.",
            "last_available_data": "The 'last_available_data' parameter is deprecated.",
            "status": (
                "The 'status' parameter is deprecated and has been moved to "
                "DashboardVersion."
            ),
            "create_run": (
                "The 'create_run' parameter is deprecated. Runs will not be supported "
                "anymore in the future"
            ),
        }

        for arg, warning_msg in deprecated_args.items():
            if arg in kwargs:
                warnings.warn(warning_msg, DeprecationWarning)

        self._api_client = DashboardAPI()

        if content is None:
            self.__slug = kwargs.get("slug")
            self.__version = (
                self.__set_version(kwargs.get("version"))
                if kwargs.get("version") is not None
                else "none"
            )
            self.__last_available_data = kwargs.get("last_available_data")
            self.__status = kwargs.get("status")
            self.__create_run = kwargs.get("create_run", False)
        else:
            self.__workspace_slug = workspace_slug
            self.__app_slug = app_slug
            self.__dashboard_slug = dashboard_slug
            self.__title = title
            self.__layout = self.__generate_content(content=content)
            self.__version: Optional[str] = None

    @property
    def version(self) -> str:
        """Returns the version of the dashboard."""
        return self.__version

    @property
    def last_available_data(self) -> Optional[Union[datetime, List[str]]]:
        """Returns Last Available Data.
        Returns:
            Optional[Union[datetime, List[str]]]: last available data
        """
        return self.__last_available_data

    def __set_version(self, version: str) -> str:
        """Get the version for the dashboard."""
        result = (
            config.DASHBOARD_VERSION
            if config.DASHBOARD_VERSION is not None
            else version
        )

        if not re.match(r"(\d+)\.(\d+)\.(\d+)", result):
            raise DashboardVersionValueError(slug=self.__slug)

        return result

    @last_available_data.setter
    def last_available_data(self, last_available_data: Optional[datetime]) -> None:
        if last_available_data is not None and not isinstance(
            last_available_data, datetime
        ):
            raise MetadataLastAvailableDataTypeError
        self.__last_available_data = last_available_data

    @property
    def _get_last_available_data(self) -> Optional[Union[int, float]]:
        if self.__last_available_data is not None and not isinstance(
            self.__last_available_data, datetime
        ):
            raise MetadataLastAvailableDataTypeError

        if self.__last_available_data is not None:
            timestamp = self.__last_available_data.timestamp()
            if len(str(int(timestamp))) == 10:
                timestamp = timestamp * 1000
            return timestamp
        return None

    def prepare(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepare the DashboardVersion object."""
        if (
            self.__version is not None
            and self.__last_available_data is not None
            and isinstance(self.__last_available_data, list)
        ):
            date = kwargs["storage"].get(
                "/".join(self.__last_available_data), default=None
            )
            if date is None:
                warnings.warn(
                    f"Cannot find `last_available_data` in path "
                    f"{self.__last_available_data}. "
                    f"Setting `last_available_data` to None."
                )
            self.__last_available_data = (
                datetime.fromtimestamp(cast(float, date)) if date is not None else date
            )

    def create_dashboard_version(self, activate: bool = False) -> None:
        """Create dashboard version in API."""
        self.__prepare()
        dashboard_input = self.build()
        response = self._api_client.create_dashboard_version(
            workspace_slug=dashboard_input.get("workspaceSlug"),
            app_slug=dashboard_input.get("appSlug"),
            dashboard_slug=dashboard_input.get("dashboardSlug"),
            layout=dashboard_input.get("layout"),
        )

        if response is not None:
            self.__version = response.get("version")
            full_path = self.__get_publish_url(response.get("version"))
            dashboard_version_response = DashboardVersionResponse(
                url_path=full_path,
                version=self.__version,
                active=response.get("active"),
                dashboard_version_id=response.get("dashboard_version_id"),
                app_slug=self.__app_slug,
                workspace_slug=self.__workspace_slug,
                dashboard_slug=self.__dashboard_slug,
            )
            if activate and not response.get("active", False):
                self._api_client.activate_dashboard_version(
                    workspace_slug=self.__workspace_slug,
                    app_slug=self.__app_slug,
                    dashboard_slug=self.__dashboard_slug,
                    version=self.__version,
                )
                dashboard_version_response.active = True
            self.__finish_publish(dashboard_version_response)

    def __finish_publish(
        self, dashboard_version_response: DashboardVersionResponse
    ) -> None:
        """Notify the user when the run ends."""
        sys.stdout.write("\n\nDashboard Successfully Published 🚀\n")
        sys.stdout.write(f"URL: {dashboard_version_response.url_path}\n\n")
        if not dashboard_version_response.active:
            sys.stdout.write(
                f"Dashboard version {dashboard_version_response.version} published "
                "without activation. "
                "To activate please do it on the URL above or run this command:\n"
                f"engineai dashboard activate {self.__workspace_slug} {self.__app_slug} "
                f"{self.__dashboard_slug} {dashboard_version_response.version}"
            )

    def __get_publish_url(self, version: str) -> str:
        platform_url = PLATFORM_URL.get(urlparse(self._api_client.url).netloc)
        path = (
            f"/preview/workspaces/{self.__workspace_slug}"
            f"/apps/{self.__app_slug}/dashboards/{self.__dashboard_slug}"
            f"?dashboard-version={version}\n\n"
        )
        url = f"{platform_url}{path}" if self._api_client.url is not None else None

        if url is None:
            msg = "URL not found"
            raise ValueError(msg)

        return url

    def __prepare(self) -> None:
        prepare_kwargs: PrepareParams = {
            "dashboard_slug": self.__dashboard_slug,
        }
        self.__layout.prepare(**prepare_kwargs)

    def __build_content(self) -> Dict[str, Any]:
        """Builds content for dashboard API."""
        return {
            "layout": {"page": self.__layout.build()},
        }

    def __generate_content(self, content: Union[Page, DashboardContent]) -> Page:
        if isinstance(content, List) and len(content) == 0:
            raise DashboardEmptyContentError
        if isinstance(content, List) and all(
            isinstance(item, Page) for item in content
        ):
            return content[0]
        if isinstance(content, Page):
            return content

        return Page(title=self.__title, content=cast(DashboardContent, content))

    def build(self) -> Dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API

        Raises:
            AttributeError: if widgets were added to dashboards but not to layout, or
                vice-versa.
        """
        return {
            "workspaceSlug": self.__workspace_slug,
            "appSlug": self.__app_slug,
            "dashboardSlug": self.__dashboard_slug,
            **self.__build_content(),
        }

    def build_versions(self) -> Dict[str, Any]:
        """[DEPRECATED] Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API

        Raises:
            AttributeError: if widgets were added to dashboards but not to layout, or
                vice-versa.
        """
        return {
            "version": self.__version,
            "createRun": self.__create_run,
        }
