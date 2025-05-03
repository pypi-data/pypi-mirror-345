"""Specs for Tab and TabSection."""

from typing import Any
from typing import Dict
from typing import List
from typing import Optional
from typing import Union

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.layout.build_item import build_item
from engineai.sdk.dashboard.layout.typings import LayoutItem
from engineai.sdk.dashboard.links.widget_field import WidgetField
from engineai.sdk.dashboard.styling.icons import Icons
from engineai.sdk.dashboard.templated_string import TemplatedStringItem
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.utils import is_valid_url

from ...interface import CollapsibleInterface
from ..selectable.base import SelectableItem
from ..selectable.base import SelectableSection


class CollapsibleTab(SelectableItem):
    """Represents an individual tab within a TabSection."""

    @type_check
    def __init__(
        self,
        *,
        label: TemplatedStringItem,
        content: Union[LayoutItem, List[LayoutItem]],
        icon: Optional[Union[Icons, WidgetField, str]] = None,
        default_selected: bool = False,
    ) -> None:
        """Constructor for Tab.

        Args:
            label: label to be displayed in tab.
            content: item to be added in tab.
            icon: tab icon.
            default_selected: set tab as default selected.
        """
        super().__init__(
            label=label, content=content, default_selected=default_selected
        )
        self.validate_icon(icon)
        self.__icon = icon

    @property
    def force_height(self) -> bool:
        """Get if the Row has a forced height from the ."""
        return self.item.force_height

    def validate_icon(self, icon: Optional[Union[Icons, WidgetField, str]]) -> None:
        """Check if the icon is valid."""
        if icon is not None and isinstance(icon, str):
            is_valid_url(icon)

    def build(self) -> Dict[str, Any]:
        """Method implemented by all factories to generate Input spec."""
        return {
            "label": build_templated_strings(items=self.label),
            "item": build_item(self.item),
            "icon": (
                build_templated_strings(
                    items=(
                        self.__icon.value
                        if isinstance(self.__icon, Icons)
                        else self.__icon
                    )
                )
                if self.__icon is not None
                else None
            ),
            "preSelected": self.default_selected,
        }


class CollapsibleTabSection(CollapsibleInterface, SelectableSection):
    """Organize dashboard content within tabs.

    The TabSection class is a crucial part of a dashboard
    layout, allowing users to organize content within tabs.

    """

    _INPUT_KEY = "tabSection"

    @type_check
    def __init__(
        self,
        *tabs: CollapsibleTab,
        expanded: bool = False,
    ) -> None:
        """Constructor for TabSection."""
        super().__init__()
        self._add_items(*tabs)
        self.expanded = expanded

    @property
    def force_height(self) -> bool:
        """Get if the Row has a forced height from the ."""
        return any(x.force_height for x in self._items)

    def build(self) -> Dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """
        return {
            "options": [tab.build() for tab in self._items],
            "expanded": self.expanded,
            "height": self.height,
        }
