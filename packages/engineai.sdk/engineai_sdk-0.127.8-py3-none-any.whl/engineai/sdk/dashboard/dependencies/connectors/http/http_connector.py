from typing import Any
from typing import Dict
from typing import Iterator
from typing import Tuple

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings


class HttpConnectorDependency(DependencyInterface):
    """Specs base for defining the Widget Dependency."""

    _INPUT_KEY = "httpDataConnector"

    def __init__(self, *, path: TemplatedStringItem, slug: str) -> None:
        """Creates dependency with a widget.

        Args:
            path: path to the data.
            slug: slug of data connector.
        """
        super().__init__()
        self.__path = path
        self.__slug = slug
        self.__dependency_id = ""

    def __iter__(self) -> Iterator[Tuple[str, Any]]:
        yield "dependency_id", self.__dependency_id
        yield "path", self.__path
        yield "slug", self.__slug

    def __hash__(self) -> int:
        return hash(self.__path)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self.__path == other.path
            and self.__dependency_id == other.dependency_id
            and self.__slug == other.slug
        )

    @property
    def path(self) -> TemplatedStringItem:
        """Return the path to the data."""
        return self.__path

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

    @property
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
            "path": build_templated_strings(items=self.__path),
        }
