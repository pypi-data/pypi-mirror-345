"""Top-level package for Dashboard Items with Link arguments."""

import re
from typing import Any
from typing import Dict
from typing import List
from typing import Set
from typing import Type
from typing import TypeVar
from typing import Union
from typing import get_args
from typing import overload

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.data import DataSource
from engineai.sdk.dashboard.interface import DuckDBConnectorInterface as DuckDBConnector
from engineai.sdk.dashboard.interface import HttpConnectorInterface as HttpConnector
from engineai.sdk.dashboard.interface import HttpInterface as Http
from engineai.sdk.dashboard.interface import (
    SnowflakeConnectorInterface as SnowflakeConnector,
)
from engineai.sdk.dashboard.templated_string import InternalDataField

from .route_link import RouteLink
from .template_string_link import TemplateStringLink
from .web_component import WebComponentLink
from .widget_field import WidgetField

SupportedTypes = Union[
    WidgetField,
    RouteLink,
    WebComponentLink,
    TemplateStringLink,
    InternalDataField,
    DataSource,
    Http,
    HttpConnector,
    DuckDBConnector,
    SnowflakeConnector,
]

T = TypeVar("T", bound=SupportedTypes)


class AbstractFactoryLinkItemsHandler(AbstractFactory):
    """Top-level package for Dashboard Items with Link arguments."""

    def __init__(self) -> None:
        """Construct for AbstractFactory class.

        This Abstract Item has the logic to get all WidgetLinks,
        associated to the class and its Children.

        Examples:
            class Child(AbstractFactoryItem):

                def __init__(label: Union[str, WidgetField]):
                    self.__label = label

            class Parent(AbstractFactoryItem):

                def __init__(title: Union[str, WidgetField], child: Child):
                    self.__title = title
                    self.__child = child

            parent = Parent(
                child=Child(label=WidgetField(widget=select_widget, field="b"))
            )

            parent.get_widget_fields() = [WidgetField(widget=select_widget, field="b")]

            In the build and publish process all the links are handle and publish.
        """
        super().__init__()
        self.__items: Dict[Type[SupportedTypes], Set[SupportedTypes]] = {}
        self.__checked_items: List[Any] = []

    def __setattr__(self, name: str, value: Any) -> None:
        super().__setattr__(name, value)
        if isinstance(value, (get_args(SupportedTypes), str)):
            self._handle_item(value)

    def _handle_item(self, value: Union[SupportedTypes, str]) -> None:
        if isinstance(value, str):
            for template_link in self._get_template_links(value):
                self.__items.setdefault(type(template_link), set()).add(template_link)
        else:
            self.__items.setdefault(type(value), set()).add(value)

    @staticmethod
    def _get_template_links(value: str) -> List[TemplateStringLink]:
        return [TemplateStringLink(result) for result in re.findall("{{(.*?)}}", value)]

    def get_items(self, item_type: Type[T]) -> Set[T]:
        """Get items of a specific type."""
        return self.__items.get(item_type, set())

    def _get_abstract_items(
        self, variable: Any
    ) -> List["AbstractFactoryLinkItemsHandler"]:
        items = (
            [variable] if isinstance(variable, AbstractFactoryLinkItemsHandler) else []
        )

        for value in vars(variable).values():
            if isinstance(value, AbstractFactory) and value not in self.__checked_items:
                self.__checked_items.append(value)
                items += self._get_abstract_items(variable=value)
            elif isinstance(value, (set, list)):
                for item in value:
                    if (
                        isinstance(item, AbstractFactory)
                        and item not in self.__checked_items
                    ):
                        self.__checked_items.append(item)
                        items += self._get_abstract_items(variable=item)

        return items

    @overload
    def get_all_items(self, item_type: Type[T]) -> Set[T]: ...

    @overload
    def get_all_items(self, *item_types: Type[T]) -> Set[T]: ...

    def get_all_items(self, *item_types: Type[T]) -> Set[T]:
        """Update items of a specific type and return them."""
        if not item_types:
            msg = "At least one item type must be specified"
            raise ValueError(msg)
        result = set()
        for item_type in item_types:
            selected_items = self.get_items(item_type)
            self.__checked_items = []

            items: List[AbstractFactoryLinkItemsHandler] = self._get_abstract_items(
                variable=self
            )
            for item in items:
                selected_items.update(item.get_items(item_type))
            result.update(selected_items)

        return result
