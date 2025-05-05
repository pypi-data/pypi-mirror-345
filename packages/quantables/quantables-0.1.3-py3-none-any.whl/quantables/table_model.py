import pandas as pd
import pint
import pint_pandas
import uncertainties
from unpaac import uncrts
from string import Formatter
from PySide6.QtCore import Qt, QAbstractTableModel

from quantables import string_utils as su


class ShorthandFormatter(Formatter):
    """Custom formatter for handling quantities with units and uncertainties."""

    def format_field(self, value, format_spec):
        if isinstance(value, uncertainties.UFloat) or isinstance(value, pint.Quantity):
            return f"{value:{format_spec}SP}"
        return str(value)


class PintUncertaintyModel(QAbstractTableModel):
    """Qt table model for displaying pandas data with units and uncertainties.

    Formats and displays `pint.Quantity` or `pint.Measurement` values,
    optionally splitting magnitude and uncertainty into separate columns.

    Args:
        dataframe: The pandas DataFrame containing the data to display.
        deconvolute: If True, separates magnitude and uncertainty into distinct columns.
        significant_digits: Number of digits to show for values with uncertainties.
        header_unit_prefix: String to prepend to units in column headers.
        header_unit_suffix: String to append to units in column headers.
        nan_string: String to display for NaN or missing values.
        pretty (bool): If True, replace "_" in labels with " " and convert to title case.
    """

    def __init__(
        self,
        dataframe,
        deconvolute: bool = False,
        significant_digits: int = 1,
        header_unit_prefix: str = su.UNIT_PREFIX,
        header_unit_suffix: str = su.UNIT_SUFFIX,
        nan_string: str = su.NAN_STRING,
        pretty: bool = True,
    ) -> None:
        super().__init__()
        self.deconvolute = deconvolute
        self.pretty = pretty
        self.significant_digits = significant_digits
        self._header_unit_prefix = header_unit_prefix
        self._header_unit_suffix = header_unit_suffix
        self._nan_string = nan_string
        self._data = dataframe
        self._data_to_display = None
        self._frmtr = ShorthandFormatter()
        self._convert_data()

    def _convert_data(self) -> None:
        """Convert the data based on deconvolution or convolution mode."""
        if self.deconvolute:
            df = self._data.uncrts.deconvolute()
        else:
            df = self._data.uncrts.convolute()
        self._data_to_display = df.pint.dequantify()

    def _transform_label(self, label: str) -> str:
        """Transform the label shown in the form based on the pretty flag."""
        if self.pretty:
            return su.pretty_title(label)
        return label

    def rowCount(self, parent=None) -> int:
        if self._data_to_display is None:
            return 0
        return self._data_to_display.shape[0]

    def columnCount(self, parent=None) -> int:
        if self._data_to_display is None:
            return 0
        return self._data_to_display.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if role == Qt.DisplayRole:
            value = self._data_to_display.iat[index.row(), index.column()]
            if pd.isna(value):
                return self._nan_string
            return self._frmtr.format(f"{{0:.{self.significant_digits}u}}", value)
        if role == Qt.TextAlignmentRole:
            return Qt.AlignRight | Qt.AlignVCenter
        return None

    def headerData(self, section, orientation, role=Qt.DisplayRole):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            measure = self._data_to_display.columns[section][0]
            title = self._transform_label(measure)
            unit = self._data_to_display.columns[section][1]
            if unit == su.NO_UNIT_STRING:
                return title
            return f"{title}{self._header_unit_prefix}{unit}{self._header_unit_suffix}"
        if role == Qt.TextAlignmentRole and orientation == Qt.Horizontal:
            return Qt.AlignTop | Qt.AlignHCenter
        return None

    def set_uncertainty_mode(self, deconvolute: bool) -> None:
        """Set the uncertainty mode (deconvolution or convolution)."""
        if self.deconvolute != deconvolute:
            self.deconvolute = deconvolute
            self._convert_data()
            self.layoutChanged.emit()
