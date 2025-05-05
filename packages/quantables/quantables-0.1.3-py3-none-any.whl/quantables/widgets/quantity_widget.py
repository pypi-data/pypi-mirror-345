from typing import Optional, Tuple, Union

import pint
from PySide6.QtWidgets import (
    QComboBox,
    QDialogButtonBox,
    QDoubleSpinBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QSizePolicy,
    QWidget,
)


# Constants for sising and data range
QUANTITY_SPINE_RANGE = (0, 1e6)
UNIT_CMBO_WIDTH = 80
STD_LINEEDIT_WIDTH = 80


def create_std_input(width: Optional[int] = None) -> Tuple[QLabel, QLineEdit]:
    """Create label and input field for standard deviation (1σ).

    Args:
        width (int | None): Optional fixed width for the QLineEdit.

    Returns:
        tuple[QLabel, QLineEdit]: A ± label and a QLineEdit for optional input.
    """
    std_label = QLabel("\u00b1")
    std_label.setSizePolicy(QSizePolicy.Minimum, QSizePolicy.Fixed)

    std_input = QLineEdit()
    std_input.setPlaceholderText("1σ (optional)")
    std_input.setToolTip("Enter standard deviation (1σ). Leave empty if unknown.")
    if width is not None:
        std_input.setFixedWidth(width)

    return std_label, std_input


def get_compatiable_units(x: pint.Unit, ureg: pint.UnitRegistry) -> set[pint.Unit]:
    """Retrieve a set of units compatible with the provided unit.

    This function checks the dimensionality of the units in the UnitRegistry and
    compares them with the dimensionality of the given unit. It returns a set of
    compatible units that are dimensionally equivalent to the input unit.

    Args:
        unit (pint.Unit): The unit whose compatible units are to be retrieved.
        x (pint.UnitRegistry): The Pint unit registry containing available units.

    Returns:
        set[pint.Unit]: A set of units that are dimensionally compatible with
            the provided unit `x`.

    Note:
        This function has been written by 'terranjp' (https://github.com/terranjp),
        and was copied from the following issue of the Pint GitHub repository:
        https://github.com/hgrecco/pint/issues/610#issuecomment-1566326356
    """
    compatible_units = set()

    for unit_str in dir(ureg):
        try:
            unit = getattr(ureg, unit_str)
        except pint.errors.UndefinedUnitError:
            continue
        if not isinstance(unit, pint.Unit):
            continue
        if hasattr(unit, "dimensionality"):
            if unit.dimensionality == x.dimensionality:
                compatible_units.add(unit)

    return compatible_units


def populate_unit_selector(
    ureg: pint.UnitRegistry, unit_selector: QComboBox, unit: str
) -> None:
    """Populate a QComboBox with units compatible with the provided unit.

    Args:
        ureg (pint.UnitRegistry): The Pint unit registry.
        unit_selector (QComboBox): The combo box to populate.
        unit (str): The unit string used as a reference for compatibility.
    """
    uobj = ureg.Unit(unit)
    compatible_units = sorted(
        {str(u) for u in get_compatiable_units(uobj, ureg)} | {str(uobj)}
    )

    unit_selector.addItems(compatible_units)
    unit_selector.setCurrentIndex(compatible_units.index(str(uobj)))


def str_to_numeric(value_str: str) -> Union[int, float]:
    """Convert a string to int if exact, else to float. Raise ValueError if fails."""
    try:
        int_value = int(value_str)
        if str(int_value) == value_str.strip():
            return int_value
    except ValueError:
        pass
    try:
        return float(value_str)
    except ValueError:
        raise ValueError(f"Cannot convert {value_str!r} to a numeric type.")


class QuantityWidget(QWidget):
    """Custom widget bundling nominal value, optional std, and unit selection.

    Args:
        ureg (pint.UnitRegistry): The Pint unit registry.
        unit (str): The reference unit for compatible unit population.
        std (bool, optional): If True, includes an input field for standard deviation.
          Defaults to True.
    """

    def __init__(
        self,
        ureg: pint.UnitRegistry,
        unit: str,
        std: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self._ureg = ureg
        self._initial_unit = unit

        self.nominal_input = QDoubleSpinBox()
        self.std_input: QLineEdit | None = None
        self.unit_selector = QComboBox()

        self.layout = QHBoxLayout()
        self._setup_ui(std)

    def _setup_ui(self, std: bool) -> None:
        self.nominal_input.setRange(*QUANTITY_SPINE_RANGE)
        self.nominal_input.setToolTip("Enter the nominal (measured) value.")
        self.nominal_input.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.layout.addWidget(self.nominal_input)

        if std:
            std_label, self.std_input = create_std_input(STD_LINEEDIT_WIDTH)
            self.layout.addWidget(std_label)
            self.layout.addWidget(self.std_input)

        self.unit_selector.setToolTip("Select the unit of measurement.")
        self.unit_selector.setFixedWidth(UNIT_CMBO_WIDTH)
        populate_unit_selector(self._ureg, self.unit_selector, self._initial_unit)
        self.layout.addWidget(self.unit_selector)

    @property
    def selected_unit(self) -> str:
        """Return the string of the currently selected unit."""
        return self.unit_selector.currentText()

    def get_layout(self) -> QHBoxLayout:
        """Return the layout for this widget."""
        return self.layout

    def get_quantity(self) -> Union[pint.Quantity, pint.Measurement]:
        """Retrieve the quantity (with or without std) as a Pint object."""
        magnitude = self.nominal_input.value()
        unit_str = self.selected_unit
        quantity = magnitude * self._ureg(unit_str)

        if self.std_input and self.std_input.text().strip():
            std_val = str_to_numeric(self.std_input.text())
            std_quantity = std_val * self._ureg(unit_str)
            measurement = self._ureg.Measurement(quantity, std_quantity)
            return measurement.to(self._initial_unit)

        return quantity.to(self._initial_unit)

    def set_quantity(self, quantity: Union[pint.Quantity, pint.Measurement]) -> None:
        """Set the provided quantity to the widget, convert value to preferred unit."""
        quant = quantity.to(self.selected_unit)

        if isinstance(quant, pint.Quantity):
            nominal = quant.magnitude
            std = None
        elif isinstance(quant, pint.Measurement):
            nominal = quant.value.magnitude
            std = quant.error.magnitude
        else:
            raise NotImplementedError(
                "Unsupported type for quantity. Expected pint.Quantity or pint.Measurement."
            )
        self.nominal_input.setValue(nominal)

        if std is not None:
            self.std_input.setText(str(std))  # type: ignore
