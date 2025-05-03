"""Spec for defining data from a duckDB connector request."""

import re
from typing import Any
from typing import Dict

from engineai.sdk.dashboard.dependencies import DuckDBConnectorDependency
from engineai.sdk.dashboard.interface import DuckDBConnectorInterface
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.templated_string import TemplatedStringItem

from ...exceptions import DataInvalidSlugError


class DuckDB(AbstractFactoryLinkItemsHandler, DuckDBConnectorInterface):
    """Spec for defining data from a duckDB connector request."""

    def __init__(self, *, query: TemplatedStringItem, slug: str) -> None:
        """Constructor for DuckDB class.

        Args:
            query: query to get data.
            slug: slug to data connector.
        """
        super().__init__()
        self.__query = query
        self.__slug = self.__set_slug(slug)
        self.__dependency = DuckDBConnectorDependency(
            query=self.__query, slug=self.__slug
        )
        self.as_dict = True

    @property
    def dependency(self) -> DuckDBConnectorDependency:
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
