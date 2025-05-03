"""Spec for defining data from a http connector request."""

import re
from typing import Any
from typing import Dict

from engineai.sdk.dashboard.dependencies import HttpConnectorDependency
from engineai.sdk.dashboard.interface import HttpConnectorInterface
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ...exceptions import DataInvalidSlugError


class HttpGet(AbstractFactoryLinkItemsHandler, HttpConnectorInterface):
    """Spec for defining data from a http connector request."""

    def __init__(
        self,
        *,
        path: TemplatedStringItem,
        slug: str,
        as_dict: bool = False,
    ) -> None:
        """Constructor for HttpGet class.

        Args:
            path: path to the data.
            slug: slug of data connector.
            as_dict: flag to return data as dictionary.
        """
        super().__init__()
        self.__path = path
        self.__slug = self.__set_slug(slug)
        self.__dependency = HttpConnectorDependency(path=self.__path, slug=self.__slug)
        self.as_dict = as_dict

    @property
    def dependency(self) -> HttpConnectorDependency:
        """Property to get the dependency object."""
        return self.__dependency

    @property
    def slug(self) -> str:
        """Return the slug."""
        return self.__slug

    @staticmethod
    def __set_slug(slug: str) -> str:
        """Set a connector slug."""
        pattern = re.compile("^[a-z0-9-_]+$")

        if (
            pattern.search(slug) is None
            or slug[-1] == "_"
            or not (3 <= len(slug) <= 36)
        ):
            raise DataInvalidSlugError(slug=slug)

        return slug

    def build(self) -> Dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return self.__dependency.build()
