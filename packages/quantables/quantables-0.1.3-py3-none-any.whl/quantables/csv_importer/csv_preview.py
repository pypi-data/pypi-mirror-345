from typing import List, Optional, Iterable

import pandas as pd
from unpaac.uncrts import create_pint_series
from PySide6.QtCore import Qt, QAbstractTableModel, QModelIndex
from PySide6.QtWidgets import (
    QAbstractItemView,
    QVBoxLayout,
    QComboBox,
    QTableView,
    QWidget,
)

from quantables import string_utils as su

CUSTOM_COMBO_TOOLTIP = "Double-click to edit and enter a custom value."


def convert_column(s: pd.Series) -> pd.Series:
    """Try to convert a pandas Series to various types."""
    # Try converting to integer
    try:
        return pd.to_numeric(s, errors="raise", downcast="integer")
    except Exception:
        pass

    # Try converting to float
    try:
        return pd.to_numeric(s, errors="raise", downcast="float")
    except Exception:
        pass

    # Try converting to datetime
    try:
        return pd.to_datetime(s, format="%Y-%m-%d %H:%M", errors="raise")
    except Exception:
        try:
            return pd.to_datetime(s, format="%Y-%m-%d", errors="raise")
        except Exception:
            pass

    # If all conversions fail, return as string
    return s.astype(str)


def populate_combo_box(
    combo: QComboBox,
    entries: Iterable[str],
    title: str | None = None,
    parent: QWidget | None = None,
) -> None:
    """Populates a QComboBox with the given entries."""
    if not isinstance(combo, QComboBox):
        raise TypeError(f"'combo' must be an instance of QComboBox ({type(combo)})")

    if not isinstance(entries, Iterable) or not all(
        isinstance(entry, str) for entry in entries
    ):
        raise ValueError("'entries' must be an iterable of strings")

    combo.clear()
    combo.setEnabled(False)

    if title is not None:
        combo.addItem(title)
        combo.setCurrentIndex(0)
        combo.model().item(0).setEnabled(False)

    for entry in entries:
        combo.addItem(entry)

    combo.setEnabled(True)


class ComboBox(QComboBox):
    """Combo box that allows to set the text by an option string."""

    def setText(self, text: str) -> None:
        """Set the current index based on text if it exists in the items."""
        index = self.findText(text)
        if index != -1:
            self.setCurrentIndex(index)


class CustomComboBox(ComboBox):
    """Combo box that becomes editable on double-click."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setEditable(False)
        self.setToolTip(CUSTOM_COMBO_TOOLTIP)

    def mouseDoubleClickEvent(self, event) -> None:
        self.setEditable(True)
        super().mouseDoubleClickEvent(event)

    def focusOutEvent(self, event) -> None:
        self.setEditable(False)
        super().focusOutEvent(event)


class DataFrameModel(QAbstractTableModel):
    """Model to wrap a pandas DataFrame for QTableView."""

    def __init__(self, data: pd.DataFrame, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._df = data

    def rowCount(self, parent=QModelIndex()) -> int:
        return self._df.shape[0]

    def columnCount(self, parent=QModelIndex()) -> int:
        return self._df.shape[1]

    def data(self, index: QModelIndex, role: int = Qt.DisplayRole):
        if not index.isValid():
            return None
        if role == Qt.DisplayRole:
            return str(self._df.iat[index.row(), index.column()])
        return None

    def headerData(
        self, section: int, orientation: Qt.Orientation, role=Qt.DisplayRole
    ):
        if role == Qt.DisplayRole:
            if orientation == Qt.Horizontal:
                return str(self._df.columns[section])
            if orientation == Qt.Vertical:
                return str(section)
        return None


class DataFrameView(QTableView):
    """QTableView for displaying and extracting data from a DataFrame with quantities."""

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self.setSelectionBehavior(QAbstractItemView.SelectColumns)
        # self.setSelectionBehavior(QAbstractItemView.SelectItems)
        self.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.setAlternatingRowColors(True)
        self.horizontalHeader().setStretchLastSection(True)
        self.verticalHeader().setVisible(False)

    @staticmethod
    def _cleanup_data(
        df: pd.DataFrame, measures: Iterable[str], units: Iterable[str]
    ) -> pd.DataFrame:
        df = df.copy()

        # assign names from measure combo boxes and drop invalid ones
        df.columns = measures
        df = df.drop(columns=su.SELECT_MEASURE, errors="ignore")

        # TODO: Implement mechanism to ensure that no duplicated columns are used
        #       Best option would be to allow selecting each measure just once!

        for col, unit in zip(measures, units):
            if col not in df.columns:
                continue

            # convert datatypes into int, float, datetime, or string
            df[col] = convert_column(df[col])

            # create pint series
            ignore_units = [su.SELECT_UNIT, su.NO_UNIT_STRING, ""]
            if pd.api.types.is_numeric_dtype and unit not in ignore_units:
                df[col] = create_pint_series(df[col], unit, name=col)

        return df

    # @staticmethod
    # def _ensure_unique_columns(df: pd.DataFrame) -> pd.DataFrame:
    #     cols = df.columns
    #     col_count = {}

    #     for i, col in enumerate(cols):
    #         if col in col_count:
    #             col_count[col] += 1
    #             df.columns.values[i] = f"{col}_{col_count[col]}"
    #         else:
    #             col_count[col] = 1

    #     return df

    def _text_from_combo(self, row_index: int) -> List[str]:
        return [
            self.indexWidget(self.model().index(row_index, col)).currentText()
            for col in range(self.model().columnCount())
        ]

    def get_frame(self) -> pd.DataFrame:
        """Retrieve the all columns."""
        df = self.model()._df.copy().iloc[2:].reset_index(drop=True)
        return self._cleanup_data(df, self.get_measures(), self.get_units())

    def get_measures(self) -> List[str]:
        """Retrieve the values of the measure combo boxes."""
        return self._text_from_combo(0)

    def get_units(self) -> List[str]:
        """Retrieve the values of the unit combo boxes."""
        return self._text_from_combo(1)

    def get_selected_frame(self) -> pd.DataFrame | None:
        """Retrieve the selected columns."""
        selected = self.selectionModel().selectedIndexes()
        if not selected:
            return None

        rows = sorted(set(index.row() - 2 for index in selected if index.row() >= 2))
        cols = sorted(set(index.column() for index in selected))

        full_df = self.model()._df.copy().iloc[2:]

        # Ensure selected rows and columns are within the bounds
        if not all(0 <= r < full_df.shape[0] for r in rows) or not all(
            0 <= c < full_df.shape[1] for c in cols
        ):
            raise ValueError("Selected rows or columns are out of bounds.")

        raw_df = full_df.iloc[rows, cols].reset_index(drop=True)

        measures = [x for i, x in enumerate(self.get_measures()) if i in cols]
        units = [x for i, x in enumerate(self.get_units()) if i in cols]

        return self._cleanup_data(raw_df, measures, units)


class CSVPreviewWidget(QWidget):
    """Widget to preview CSV data with measure and unit selection in the first rows.

    Displays combo boxes in the first rows of a CSV preview table to assign measures
    and units to columns. Optionally allows custom entries if enabled.

    Args:
        measures: List of available measure names for selection.
        units: List of available unit names for selection.
        allow_custom: If True, combo boxes are editable to allow custom input.
        parent: Optional parent widget.
    """

    def __init__(
        self,
        measures: List[str],
        units: List[str],
        allow_custom: bool = False,
        parent: Optional[QWidget] = None,
    ) -> None:
        super().__init__(parent)
        self.measures = measures
        self.units = self._prepare_units(units)
        self.allow_costom = allow_custom

        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.table_view = DataFrameView(self)

        self.layout.addWidget(self.table_view)

        self._data: Optional[pd.DataFrame] = None
        self.model: Optional[DataFrameModel] = None

    def _create_combo(self) -> CustomComboBox | ComboBox:
        if self.allow_costom:
            return CustomComboBox(self)
        return ComboBox(self)

    def _populate(self) -> None:
        """Populate the table view with the given DataFrame."""
        df = self._data
        df_with_empty_rows = pd.concat(
            [pd.DataFrame([[""] * df.shape[1]] * 2, columns=df.columns), df],
            ignore_index=True,
        )
        self.model = DataFrameModel(df_with_empty_rows, self.table_view)
        self.table_view.setModel(self.model)

        # Add ComboBoxes to first two rows
        for col in range(df.shape[1]):
            measure_combo = self._create_combo()
            populate_combo_box(
                measure_combo, self.measures, title=su.SELECT_MEASURE, parent=self
            )
            self.table_view.setIndexWidget(self.model.index(0, col), measure_combo)

            unit_combo = self._create_combo()
            populate_combo_box(unit_combo, self.units, title=su.SELECT_UNIT, parent=self)
            self.table_view.setIndexWidget(self.model.index(1, col), unit_combo)

    def _prepare_units(self, units: list[str]) -> list[str]:
        """Ensure 'No Unit' is present at the beginning of the units list."""
        if su.NO_UNIT_STRING not in units:
            units = [su.NO_UNIT_STRING] + units
        return units

    def _set_combos(
        self, values: Iterable[str], row_index: int, valid_strings: Iterable[str]
    ) -> None:
        if len(values) != self.model.columnCount():
            raise ValueError("Mismatch between provided values and number of columns.")
        for col, value in enumerate(values):
            if value in valid_strings:
                combo = self.table_view.indexWidget(self.model.index(row_index, col))
                combo.setText(value)

    def apply_measures(self, measures: Iterable[str]) -> None:
        """Set CSV measure strings to measure combos, if in measure definitions."""
        self._set_combos(values=measures, row_index=0, valid_strings=self.measures)

    def apply_units(self, units: Iterable[str]) -> None:
        """Set CSV unit strings to measure combos, if in measure definitions."""
        self._set_combos(values=units, row_index=1, valid_strings=self.units)

    def set_data(
        self,
        data: pd.date_range,
        measures: Optional[Iterable[str]] = None,
        units: Optional[Iterable[str]] = None,
    ) -> None:
        self._data = data
        self._populate()
        if measures is not None:
            self.apply_measures(measures)
        if units is not None:
            self.apply_units(units)
