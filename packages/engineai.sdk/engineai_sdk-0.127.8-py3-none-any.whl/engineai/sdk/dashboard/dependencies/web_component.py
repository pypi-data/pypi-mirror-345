"""SDK Dashboard Web Component Dependency."""

from typing import Any
from typing import Dict
from typing import Iterator
from typing import List
from typing import Optional
from typing import Tuple

from engineai.sdk.dashboard.base import DependencyInterface
from engineai.sdk.dashboard.decorator import type_check


class WebComponentDependency(DependencyInterface):
    """Web Component Dependency."""

    _INPUT_KEY = "webComponent"

    @type_check
    def __init__(self, path: List[str]) -> None:
        """Constructor for WebComponentDependency Class.

        Args:
            path: path to the web component. Represents the path to the data injected
                by the web component.
        """
        self.__field: Optional[str] = path.pop(-1) if len(path) >= 2 else None
        self.__path = path
        self.__dependency_id = f"web_component_{'_'.join(path)}"

    def __str__(self) -> str:
        return (
            f"{{{{{self.dependency_id}.{self.__field}}}}}"
            if self.__field is not None
            else f"{{{{{self.dependency_id}}}}}"
        )

    def __iter__(self) -> Iterator[Tuple[str, str]]:
        yield "dependency_id", self.__dependency_id
        yield "field", self.__field or ""

    def __hash__(self) -> int:
        return hash(self.__dependency_id)

    def __eq__(self, other: object) -> bool:
        return (
            isinstance(other, type(self))
            and self.__dependency_id == other.dependency_id
            and self.__field == other.field
        )

    @property
    def dependency_id(self) -> str:
        """Returns dependency id."""
        return self.__dependency_id

    @property
    def field(self) -> str:
        """Returns field."""
        return self.__field or ""

    def build_item(self) -> Dict[str, Any]:
        """Build item."""
        return {
            "name": self.__dependency_id,
            "path": ".".join(self.__path),
        }

    def build(self) -> Dict[str, Any]:
        """Method to build specs."""
        return self.build_item()
