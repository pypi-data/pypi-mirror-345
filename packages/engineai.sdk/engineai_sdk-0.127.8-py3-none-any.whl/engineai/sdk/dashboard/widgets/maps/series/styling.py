"""Spec to style a line series."""

import warnings
from typing import Any
from typing import Dict
from typing import Optional

import pandas as pd

from engineai.sdk.dashboard.decorator import type_check
from engineai.sdk.dashboard.styling.color.palette import Palette
from engineai.sdk.dashboard.styling.color.single import Single
from engineai.sdk.dashboard.styling.color.spec import build_color_spec
from engineai.sdk.dashboard.styling.color.typing import ColorSpec
from engineai.sdk.dashboard.templated_string import build_templated_strings
from engineai.sdk.dashboard.widgets.components.charts.styling.enums import MarkerSymbol
from engineai.sdk.dashboard.widgets.maps.exceptions import MapColumnDataNotFoundError


class SeriesStyling:
    """Style numeric series appearance on map.

    Style the appearance of numeric series on a map,
    including color specifications and data column mapping for
    gradients or discrete maps.
    """

    @type_check
    def __init__(
        self,
        *,
        color_spec: Optional[ColorSpec] = None,
        data_column: Optional[str] = None,
    ) -> None:
        """Constructor for SeriesStyling.

        Args:
            color_spec: spec for coloring area
            data_column: name of column in pandas dataframe(s) used for color spec if
                a gradient is used. Optional for single colors.

        Raises:
            ValueError: if data_column is set and color_spec is Single.
        """

        super().__init__()
        self.__color_spec = color_spec or Palette.AQUA_GREEN
        self.__data_column = data_column
        if self.__data_column and isinstance(color_spec, (Single, str, Palette)):
            msg = f"data_column argument will not be set if color_spec is {color_spec.__class__.__name__}"
            warnings.warn(msg, UserWarning)

    def validate(
        self,
        *,
        data: pd.DataFrame,
    ) -> None:
        """Validate if dataframe that will be used for column contains required columns.

        Args:
            data: pandas dataframe which will be used for table

        Raises:
            ValueError: if data does not contain data_column
        """
        if (
            not isinstance(self.__color_spec, (Single, str, Palette))
            and self.__data_column
            and self.__data_column not in data.columns
        ):
            raise MapColumnDataNotFoundError(column_data=self.__data_column)

    def build(self) -> Dict[str, Any]:
        """Method implemented by all factories to generate Input spec.

        Returns:
            Input object for Dashboard API
        """

        return {
            "colorSpec": build_color_spec(spec=self.__color_spec),
            "markerSymbol": MarkerSymbol.CIRCLE.value,
            "valueKey": (
                build_templated_strings(items=self.__data_column)
                if self.__data_column is not None
                else None
            ),
        }
