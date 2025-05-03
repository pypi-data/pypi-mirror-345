"""Internal SDK WebComponent Link."""

from typing import List
from typing import Union

from engineai.sdk.dashboard.base import AbstractLink
from engineai.sdk.dashboard.dependencies.web_component import WebComponentDependency


class WebComponentLink(AbstractLink):
    """WebComponentLink is a link to a web component."""

    def __init__(self, path: Union[str, List[str]]) -> None:
        """Constructor for WebComponentLink Class.

        Args:
            path: path to the web component data. Represents the path to the data
                injected, e.g. ['path', 'to', 'data'], where 'data' is the field
                to be used.
        """
        self.__dependency = WebComponentDependency(
            path=path if isinstance(path, List) else [path]
        )

    @property
    def dependency(self) -> WebComponentDependency:
        """Returns dependency."""
        return self.__dependency

    def _generate_templated_string(self, *, selection: int = 0) -> str:  # noqa
        """Generates template string to be used in dependency."""
        return str(self.__dependency)
