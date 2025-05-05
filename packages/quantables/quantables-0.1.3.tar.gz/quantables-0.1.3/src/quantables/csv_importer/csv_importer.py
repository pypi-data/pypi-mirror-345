import pandas as pd
from typing import Mapping
import logging

from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QVBoxLayout,
    QDialog,
    QPushButton,
    QMessageBox,
    QSizePolicy,
    QSpacerItem,
    QWidget,
)

import quantables.string_utils as su
from .csv_widgets import CSVSelectorWidget, CSVOptionsWidget
from .csv_preview import CSVPreviewWidget

BUTTON_WIDTH = 100

logger = logging.getLogger(__name__)


class CSVImporterDialog(QDialog):
    """Dialog for importing CSV data with unit-aware parsing and customization.

    Allows users to:
      - Select and load a CSV file.
      - Preview and assign measures and units to columns.
      - Optionally edit measure/unit values or select a specific region.
      - Import the data as a pandas DataFrame with `pint` quantities applied.

    Double-clicking enables custom editing of combo boxes when allowed.

    Args:
        measures: A mapping of measure names to their default units.
        file_path: Optional path to a CSV file to pre-load.
        allow_custom: If True, allows custom editing of measure/unit values.
        allow_selection: If True, enables importing a selected region only.
        file_selector_icon: Optional icon for the file selection button.
        header_unit_prefix: String to place before the unit in the header.
        header_unit_suffix: String to place after the unit in the header.
        window_title: The title displayed on the dialog window.
        parent: Optional parent widget.
    """

    def __init__(
        self,
        measures: Mapping[str, str | None] | None = None,
        file_path: str | None = None,
        allow_custom: bool = False,
        allow_selection: bool = False,
        file_selector_icon: QIcon | None = None,
        header_unit_prefix: str = su.UNIT_PREFIX,
        header_unit_suffix: str = su.UNIT_SUFFIX,
        window_title: str = "CSV Importer",
        parent: QWidget | None = None,
    ) -> None:
        super().__init__(parent)
        self.setWindowTitle(window_title)
        self.resize(800, 600)

        if measures is None:
            allow_custom = True
            measures = {}

        self._allow_custom = allow_custom
        self._allow_selection = allow_selection
        self._header_unit_prefix = header_unit_prefix
        self._header_unit_suffix = header_unit_suffix
        self._data: pd.DataFrame | None = None
        self._valid_measures = measures

        self.file_path = file_path
        self.result: pd.DataFrame | None = None

        self.layout: QVBoxLayout = QVBoxLayout(self)

        # Pre-declare widget attributes
        self.file_selector: CSVSelectorWidget | None = None
        self.csv_options: CSVOptionsWidget | None = None
        self.preview: CSVPreviewWidget | None = None
        self.import_btn: QPushButton | None = None
        self.import_all_btn: QPushButton | None = None

        self._setup_ui(file_selector_icon)

        if file_path:
            self.show_file()

    def _create_import_button_box(self, button_width: int = BUTTON_WIDTH) -> None:
        """Create and add a widget with 'Import Selection', 'Import Table', and 'Cancel' buttons."""
        btn_widget = QWidget(self)
        btn_layout = QHBoxLayout(btn_widget)

        buttons = []
        if self._allow_selection:
            self.import_btn = QPushButton("Import Selection")
            self.import_btn.clicked.connect(self.import_selected_frame)
            self.import_btn.setEnabled(False)
            buttons.append(self.import_btn)
        self.import_all_btn = QPushButton("Import Table")
        self.import_all_btn.clicked.connect(self.import_frame)
        self.import_all_btn.setEnabled(False)
        buttons.append(self.import_all_btn)
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        buttons.append(cancel_btn)

        btn_layout.addItem(
            QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        )

        for btn in buttons:
            btn.setFixedWidth(button_width)
            btn_layout.addWidget(btn)

        self.layout.addWidget(btn_widget)

    def _handle_file_selected(self, file_path: str) -> None:
        self.file_path = file_path
        self.show_file()

    def _load_data(self) -> None:
        try:
            self._data = pd.read_csv(
                self.file_path,
                delimiter=self.csv_options.delimiter,
                encoding=self.csv_options.encoding,
                header=0 if self.csv_options.has_headers else None,
            )
            logger.debug(f"Loaded CSV with shape: {self._data.shape}")

        except Exception as e:
            logger.exception("Error loading CSV file.")
            QMessageBox.warning(self, "Reading Error", str(e))

    def _populate_preview(self) -> None:
        """Populate the preview table with the given DataFrame."""
        data = self._data.copy()

        def extract_row_if_needed(row_index: int, is_enabled: bool) -> pd.Series:
            """Helper method to extract a row if required."""
            if is_enabled:
                row_data = data.loc[row_index]
                data.drop(index=row_index, inplace=True)
                return row_data

        measures_row = extract_row_if_needed(0, self.csv_options.has_headers)
        if measures_row is not None:
            data.columns = measures_row

        units_row = extract_row_if_needed(1, self.csv_options.has_units)
        if units_row is not None:
            data.columns = [
                f"{c}{self._header_unit_prefix}{u}{self._header_unit_suffix}"
                for c, u in zip(data.columns, units_row)
            ]

        self.preview.set_data(data, measures=measures_row, units=units_row)

    def _setup_ui(self, file_selector_icon: QIcon | None) -> None:
        # File selector
        if self.file_path is None:
            self.file_selector = CSVSelectorWidget(self, icon=file_selector_icon)
            self.file_selector.fileSelected.connect(self._handle_file_selected)
            self.layout.addWidget(self.file_selector)

        # Options
        self.csv_options = CSVOptionsWidget(parent=self)
        self.csv_options.parsingSettingsChanged.connect(self.show_file)
        self.csv_options.conversionSettingsChanged.connect(self._populate_preview)
        self.csv_options.set_conversion_enabled(False)
        self.layout.addWidget(self.csv_options)

        # Create and add the preview table.
        self.preview = CSVPreviewWidget(
            measures=self._valid_measures.keys(),
            units=[u for u in self._valid_measures.values() if u is not None],
            allow_custom=self._allow_custom,
            parent=self,
        )
        self.layout.addWidget(self.preview)

        # Import buttons
        self._create_import_button_box()

    def get_frame(self) -> pd.DataFrame | None:
        """Return the imported data as DataFrame."""
        return self.result

    def _set_result(
        self, data: pd.DataFrame, msg_prefix="Imported data with shape: "
    ) -> None:
        """Set provided dataframe to results attribute and accept the dialog."""
        if data is not None:
            self.result = data
            logger.info(f"{msg_prefix}{data.shape}")
            self.accept()

    def _verify_result(self, data: pd.DataFrame) -> bool:
        """Verify that the valid measures are in the df and ensure mapped units."""
        for col, unit in self._valid_measures.items():
            if col not in data.columns:
                QMessageBox.critical(
                    self,
                    "Data Import Error",
                    f"{str(col)!r} column not assigned to source data.",
                )
                return False
            if unit is not None:
                try:
                    data[col] = data[col].pint.to(unit)
                except Exception as e:
                    QMessageBox.critical(
                        self, "Data Import Error", f"Invalid unit selected: {e}"
                    )
                    return False
        return True

    def import_frame(self) -> None:
        """Import the valid measure columns from the table.

        The assignment of all valid_measure keys is required.
        The data are converted to the corresponding unit.
        """
        df = self.preview.table_view.get_frame()
        if df is not None:
            if self._verify_result(df):
                # Use only the valid measure columns of the retrived data
                self._set_result(df[list(self._valid_measures.keys())])

    def import_selected_frame(self) -> None:
        """Import only the data from the selected area in the table."""
        df = self.preview.table_view.get_selected_frame()
        self._set_result(df)

    def show_file(self) -> None:
        """Load the CSV file and populate the preview with measures, units, and data."""
        self._load_data()
        self._populate_preview()
        self.csv_options.set_conversion_enabled(True)
        self.import_all_btn.setEnabled(True)
        if self._allow_selection:
            self.import_btn.setEnabled(True)
