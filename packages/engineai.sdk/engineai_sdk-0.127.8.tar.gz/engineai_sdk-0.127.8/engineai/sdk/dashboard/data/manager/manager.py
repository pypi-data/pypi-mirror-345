"""Class to manage component's data and dependencies."""

import re
from copy import copy
from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Set
from typing import Type
from typing import Union
from typing import cast

import pandas as pd
from typing_extensions import Unpack

from engineai.sdk.dashboard.abstract.selectable_widgets import AbstractSelectWidget
from engineai.sdk.dashboard.abstract.typing import PrepareParams
from engineai.sdk.dashboard.dependencies import WidgetSelectDependency
from engineai.sdk.dashboard.links import RouteLink
from engineai.sdk.dashboard.links import WidgetField
from engineai.sdk.dashboard.links.abstract import AbstractFactoryLinkItemsHandler
from engineai.sdk.dashboard.links.template_string_link import TemplateStringLink
from engineai.sdk.dashboard.links.web_component import WebComponentLink
from engineai.sdk.dashboard.templated_string import InternalDataField
from engineai.sdk.dashboard.widgets.exceptions import (
    WidgetTemplateStringWidgetNotFoundError,
)

from ...base import DependencyInterface
from ...dependencies.datastore import DashboardStorage
from ..connectors import DuckDB
from ..connectors import HttpGet
from ..connectors import Snowflake
from ..decorator import DataSource
from ..decorator import OperationItem
from ..enums import StorageType
from ..http import Http
from .interface import DependencyManagerInterface
from .interface import StaticDataType

DataType = Union[DataSource, Http, HttpGet, DuckDB, Snowflake]


class DependencyManager(AbstractFactoryLinkItemsHandler, DependencyManagerInterface):
    """Class to manage component's data and dependencies."""

    def __init__(
        self,
        data: Optional[Union[DataType, StaticDataType]] = None,
        base_path: Optional[str] = None,
    ) -> None:
        """Constructor to manage components data.

        Args:
            data: data for the widget.
                Can be a pandas dataframe or a dictionary depending on the widget type,
                or Storage object if the data is to be retrieved from a storage.
            base_path: data storage base path.
        """
        super().__init__()
        self.__dependencies: Set[DependencyInterface] = set()
        self._data = self.__set_data(data=data, base_path=base_path)
        self._json_data = (
            data
            if isinstance(data, pd.DataFrame)
            else pd.DataFrame([data])
            if isinstance(data, Dict)
            else None
        )

    @property
    def dependencies(self) -> Set[DependencyInterface]:
        """Returns dependencies of widget.

        Returns:
            Set[DependencyInterface]: dependencies of widget
        """
        return self.__dependencies

    def __set_data(
        self,
        data: Optional[Union[DataType, StaticDataType]],
        base_path: Optional[str] = None,
    ) -> Optional[DataType]:
        if data is None:
            return None
        if isinstance(data, (Http, HttpGet, DuckDB, Snowflake)):
            data.dependency.dependency_id = self.dependency_id
            return data
        data = (
            data
            if isinstance(data, DataSource)
            else DataSource(data, base_path=base_path)
        )
        data.component = self
        return data

    @property
    def data(
        self,
    ) -> Union[Set[DataSource], Set[Http], Set[HttpGet], Set[DuckDB], Set[Snowflake]]:
        """Returns data of widget.

        Returns:
            DataType: data of widget
        """

        return self.get_all_items(
            type(self._data) if self._data is not None else DataSource
        )

    # TODO: to be removed when datasources are removed completely
    @property
    def has_http_data(self) -> bool:
        """Returns True if widget has http data.

        Returns:
            bool: True if widget has http data
        """
        return isinstance(self._data, Http)

    @property
    def has_http_connector_data(self) -> bool:
        """Returns True if widget has http data.

        Returns:
            bool: True if widget has http data
        """
        return isinstance(self._data, HttpGet)

    @property
    def has_duck_db_connector_data(self) -> bool:
        """Returns True if widget has duckDb data.

        Returns:
            bool: True if widget has duckDb data
        """
        return isinstance(self._data, DuckDB)

    @property
    def has_snowflake_connector_data(self) -> bool:
        """Returns True if widget has snowflake data.

        Returns:
            bool: True if widget has snowflake data
        """
        return isinstance(self._data, Snowflake)

    def _prepare_dependencies(self, **kwargs: Unpack[PrepareParams]) -> None:
        """Prepares dependencies for widget."""
        page_id = re.sub(r"\W+", "", kwargs["page"].path)
        self.__set_internal_data_field()
        self.__set_template_links_widgets(**kwargs)
        self.__set_storage(**kwargs)
        self.__prepare_template_dependencies()
        self.__prepare_widget_fields()
        self.__prepare_widget_dependencies(page_id)
        self.__prepare_dependencies()

    def store_data(
        self, write: bool, metadata: Set[str], **kwargs: Unpack[PrepareParams]
    ) -> None:
        """Stores data in widget."""
        for data_source in self.get_all_items(DataSource):
            data_source.storage_type = kwargs.get("storage_type")
            data_source(
                storage_config=kwargs["storage"],
                write_keys=write,
                metadata=metadata,
            )

    def build_datastore_dependencies(self) -> List[Any]:
        """Build datastore dependencies."""
        return [
            self.__build_dependency(dependency) for dependency in self.__dependencies
        ]

    @staticmethod
    def __build_dependency(dependency: DependencyInterface) -> Dict[str, Any]:
        return {
            dependency.input_key: dependency.build(),
        }

    def __prepare_widget_dependencies(self, page_id: str) -> None:
        for dependency in self.__dependencies:
            if (
                isinstance(dependency, WidgetSelectDependency)
                and page_id
                and not dependency.widget_id.endswith(page_id)
            ):
                dependency.widget_id = f"{dependency.widget_id}_{page_id}"

    def __prepare_dependencies(self) -> None:
        for item in self.get_all_items(
            HttpGet, DuckDB, Snowflake, WebComponentLink, RouteLink, Http
        ):
            dependency = item.dependency
            self.__dependencies.add(dependency)
            if isinstance(item, Http) and dependency.operations is not None:
                self.__add_operations_dependencies(
                    operations=dependency.operations,
                )

    def __prepare_widget_fields(self) -> None:
        for widget_field in self.get_all_items(WidgetField):
            dependency = widget_field.link_component.select_dependency()
            self.__dependencies.add(cast(WidgetSelectDependency, dependency))

    def __prepare_template_dependencies(self) -> None:
        for template_link in self.get_all_items(TemplateStringLink):
            if template_link.is_widget_field():
                dependency = template_link.component.select_dependency(
                    dependency_id=template_link.widget_id
                )

                self.__dependencies.add(
                    cast(
                        WidgetSelectDependency,
                        dependency,
                    )
                )
            elif template_link.is_route_link():
                route_link = template_link.route_link
                self.__dependencies.add(route_link.dependency)
            elif template_link.is_web_component_link():
                self.__dependencies.add(template_link.web_component_link.dependency)

    def __set_internal_data_field(self) -> None:
        for internal_data_field in self.get_all_items(InternalDataField):
            if internal_data_field.dependency_id == "":
                internal_data_field.set_dependency_id(dependency_id=self.dependency_id)

    def __set_template_links_widgets(
        self,
        **kwargs: Unpack[PrepareParams],
    ) -> None:
        dashboard_slug = kwargs["dashboard_slug"]
        selectable_widgets: Dict[str, AbstractSelectWidget] = kwargs[
            "selectable_widgets"
        ]
        for template_link in self.get_all_items(TemplateStringLink):
            if template_link.is_web_component_link():
                continue
            if template_link.is_widget_field():
                if template_link.widget_id not in selectable_widgets:
                    raise WidgetTemplateStringWidgetNotFoundError(
                        slug=dashboard_slug,
                        widget_id=self.data_id,
                        template_widget_id=template_link.widget_id,
                    )
                template_link.component = cast(
                    AbstractSelectWidget,
                    selectable_widgets.get(template_link.widget_id),
                )
            elif template_link.is_route_link():
                template_link.component = kwargs["page"].route

    def __set_storage(self, **kwargs: PrepareParams) -> None:
        """Sets the data storage based on widget dependency id(s)."""
        for data_source in self.get_all_items(DataSource):
            if kwargs.get("storage_type") is not None:
                data_source.storage_type = kwargs.get("storage_type")
                self.__add_link_dependencies(data_source=data_source)
                dependency: DashboardStorage = self.__set_dependency(data_source)

                self.__dependencies.add(dependency)

                if data_source.operations is not None:
                    self.__add_operations_dependencies(
                        operations=data_source.operations,
                    )

    def __set_dependency(self, data_source: DataSource) -> DashboardStorage:
        _storage_type: Type[DashboardStorage] = StorageType.get_storage_class(
            data_source.storage_type.value
        )
        return _storage_type(
            dependency_id=data_source.component.dependency_id,
            series_id=self.__generate_series_id(data_source),
            operations=data_source.operations,
        )

    @staticmethod
    def __generate_series_id(data_source: DataSource) -> str:
        if len(data_source.args) > 0:
            store_id_templates: List[str] = [str(link) for link in data_source.args]

            series_id = (
                store_id_templates[0]
                if len(store_id_templates) == 1
                else data_source.separator.join(store_id_templates)
            )
            return f"{data_source.base_path}/{series_id}"
        return data_source.base_path

    def __add_link_dependencies(self, data_source: DataSource) -> None:
        for link in data_source.args:
            if isinstance(link, WidgetField):
                dependency = cast(
                    WidgetSelectDependency, link.link_component.select_dependency()
                )
                self.__dependencies.add(dependency)

            elif isinstance(link, RouteLink):
                new_link = copy(link)
                new_link.dependency.path = data_source.base_path
                self.__dependencies.add(new_link.dependency)

    def __add_operations_dependencies(
        self,
        operations: List[OperationItem],
    ) -> None:
        for operation in operations:
            for dependency in operation.dependencies:
                self.__dependencies.add(dependency)
