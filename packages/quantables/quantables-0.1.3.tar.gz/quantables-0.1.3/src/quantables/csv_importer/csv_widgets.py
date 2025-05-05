from typing import List, Optional
from PySide6.QtCore import Signal
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QFileDialog,
    QFormLayout,
    QGridLayout,
    QGroupBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QSizePolicy,
    QVBoxLayout,
    QWidget,
)

DELIMITERS = [",", ";", "\t", "|"]
ENCODINGS = ["utf-8", "latin1", "ascii", "utf-16"]
FILE_SELECTOR_TEXT = "..."


def select_csv_file(parent: QWidget | None = None) -> str:
    """Open a file dialog and offer CSV file selection."""
    file_path, _ = QFileDialog.getOpenFileName(
        parent, "Select CSV File", "", "CSV Files (*.csv)"
    )
    if not file_path:
        return ""

    return file_path


class CSVOptionsWidget(QWidget):
    """Widget for configuring CSV parsing and conversion options.

    Provides controls for selecting the delimiter and encoding used in a CSV file,
    along with checkboxes for indicating the presence of header and unit rows.

    Args:
        delimiters: List of delimiter options to populate the delimiter combo box.
        encodings: List of encoding options to populate the encoding combo box.
        parent: Optional parent widget.

    Emits:
        parsingSettingsChanged: Emitted when delimiter or encoding selection changes.
        conversionSettingsChanged: Emitted when header or unit row checkboxes change.
    """

    conversionSettingsChanged = Signal()
    parsingSettingsChanged = Signal()

    def __init__(
        self,
        delimiters: List[str] = DELIMITERS,
        encodings: List[str] = ENCODINGS,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)

        parsing_group = QGroupBox("Parsing")
        parsing_grid = QGridLayout()

        parsing_grid.addWidget(QLabel("Delimiter:"), 0, 0)
        self._delimiter_combi = QComboBox()
        self._delimiter_combi.addItems(delimiters)
        self._delimiter_combi.currentTextChanged.connect(
            self._handle_parsing_settings_changed
        )
        parsing_grid.addWidget(self._delimiter_combi, 0, 1)

        parsing_grid.addWidget(QLabel("Encoding:"), 1, 0)
        self._encoding_combo = QComboBox()
        self._encoding_combo.addItems(encodings)
        self._encoding_combo.currentTextChanged.connect(
            self._handle_parsing_settings_changed
        )
        parsing_grid.addWidget(self._encoding_combo, 1, 1)

        parsing_group.setLayout(parsing_grid)
        layout.addWidget(parsing_group)

        self._conversion_group = QGroupBox("Conversion")
        conversion_grid = QGridLayout()

        self._header_checkbox = QCheckBox("First row contains headers")
        self._header_checkbox.clicked.connect(self._handle_converstion_settings_changed)
        conversion_grid.addWidget(self._header_checkbox, 2, 0, 1, 2)

        self._unit_checkbox = QCheckBox("Second row contains units")
        self._unit_checkbox.clicked.connect(self._handle_converstion_settings_changed)
        conversion_grid.addWidget(self._unit_checkbox, 3, 0, 1, 2)

        self._conversion_group.setLayout(conversion_grid)
        layout.addWidget(self._conversion_group)

    def _handle_converstion_settings_changed(self, *args, **kwargs) -> None:
        self.conversionSettingsChanged.emit()

    def _handle_parsing_settings_changed(self, *args, **kwargs) -> None:
        self.parsingSettingsChanged.emit()

    @property
    def delimiter(self) -> bool:
        return self._delimiter_combi.currentText()

    @property
    def encoding(self) -> bool:
        return self._encoding_combo.currentText()

    @property
    def has_headers(self) -> bool:
        return self._header_checkbox.isChecked()

    @property
    def has_units(self) -> bool:
        return self._unit_checkbox.isChecked()

    def set_conversion_enabled(self, enabled: bool) -> None:
        """Enable or disable the conversion group box."""
        self._conversion_group.setEnabled(enabled)


class CSVSelectorWidget(QWidget):
    """Widget that allows users to select a CSV file via a file dialog.

    Args:
        title: The dialog title shown when selecting a file.
        icon: Optional icon to display on the file selection button.
        parent: Optional parent widget.

    Emits:
        fileSelected (str): Emitted with the selected file path when a file is chosen.
    """

    fileSelected = Signal(str)

    def __init__(
        self,
        title: str = "CSV File",
        icon: QIcon | None = None,
        parent: Optional[QWidget] = None,
    ):
        super().__init__(parent)

        layout = QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)

        group_box = QGroupBox(title)

        self.file_path_input = QLineEdit()
        self.file_path_input.setPlaceholderText("No file selected")
        self.file_path_input.setReadOnly(True)

        self.browse_button = QPushButton(FILE_SELECTOR_TEXT)
        if icon is not None:
            self.browse_button.setIcon(icon)
            self.browse_button.setText("")
        self.browse_button.setToolTip("Select CSV File")
        self.browse_button.setStyleSheet("padding-left: 5px; padding-right: 5px;")
        self.browse_button.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Preferred)
        self.browse_button.adjustSize()
        self.browse_button.clicked.connect(self._handle_file_selection)

        file_layout = QHBoxLayout()
        file_layout.addWidget(self.file_path_input)
        file_layout.addWidget(self.browse_button)

        form_layout = QFormLayout()
        form_layout.addRow(file_layout)
        # form_layout.addRow("CSV File:", file_layout)

        group_box.setLayout(form_layout)
        layout.addWidget(group_box)
        self.setLayout(layout)

    def _handle_file_selection(self) -> None:
        file_path = select_csv_file(self)
        if file_path:
            self.set_file_path(file_path)

    def set_file_path(self, file_path: str) -> None:
        """Set a path to the line edit and emit fileSelected signal."""
        self.file_path_input.setText(file_path)
        self.fileSelected.emit(file_path)
