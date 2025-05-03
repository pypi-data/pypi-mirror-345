"""Spec for SingleColor class."""

from typing import Any
from typing import Dict
from typing import Union

from engineai.sdk.dashboard.base import AbstractFactory
from engineai.sdk.dashboard.decorator import type_check

from .palette import Palette


class Single(AbstractFactory):
    """Class for creating a single color instance.

    Create a class representing a single color within
    a palette for a Timeseries widget.
    """

    @type_check
    def __init__(self, color: Union[str, Palette]) -> None:
        """Constructor for Single.

        Args:
            color: a color from Palette or a hex color string (including transparency alpha).
        """
        super().__init__()
        self.__color = (
            color.color if isinstance(color, Palette) else self._generate_color(color)
        )

    def _generate_color(self, color: str) -> str:
        """Generates color string."""
        # Check if the code has the # prefix
        final_color = color if color.startswith("#") else f"#{color}"

        # Check alpha
        if len(final_color) == 7:
            final_color += "ff"
        return final_color

    def build(self) -> Dict[str, Any]:
        """Builds spec for dashboard API.

        Returns:
            Input object for Dashboard API
        """
        return {
            "customColor": self.__color,
        }
