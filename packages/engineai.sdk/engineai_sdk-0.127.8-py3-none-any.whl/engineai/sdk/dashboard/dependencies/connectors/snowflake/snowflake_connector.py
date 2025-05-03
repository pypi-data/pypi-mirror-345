from typing import Any
from typing import Dict
from typing import Iterator
from typing import Tuple

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings


class SnowflakeConnectorDependency(DependencyInterface):
    """Specs base for defining the Widget Dependency."""

    _INPUT_KEY = "snowflake"

    def __init__(self, *, query: TemplatedStringItem, slug: str) -> None:
        """Creates dependency with a widget.

        Args:
            query: query to get data.
            slug: slug to data connector.
        """
        super().__init__()
        self.__query = query
        self.__slug = slug
        self.__dependency_id = ""

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        yield "dependency_id", self.__dependency_id
        yield "query", self.__query
        yield "slug", self.__slug

    def __hash__(self) -> int:
        return hash(self.__query)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self.__query == other.query
            and self.__dependency_id == other.dependency_id
            and self.__slug == other.slug
        )

    @property
    def query(self) -> TemplatedStringItem:
        """Return the query to get data."""
        return self.__query

    @property
    def dependency_id(self) -> str:
        """Return Dependency ID."""
        if self.__dependency_id == "":
            msg = "Dependency ID not set."
            raise NotImplementedError(msg)
        return self.__dependency_id

    @dependency_id.setter
    def dependency_id(self, dependency_id: str) -> None:
        """Set Dependency ID."""
        self.__dependency_id = dependency_id

    def slug(self) -> str:
        """Return the slug."""
        return self.__slug

    def build(self) -> Dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Any: Input object for Dashboard API
        """
        return {
            "name": self.dependency_id,
            "dataConnectorSlug": self.__slug,
            "query": build_templated_strings(items=self.__query),
        }
