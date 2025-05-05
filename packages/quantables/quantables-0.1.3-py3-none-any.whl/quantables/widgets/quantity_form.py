from typing import Union, List, Dict, Set

import pint
from PySide6.QtWidgets import QFormLayout, QGroupBox, QWidget

from quantables.string_utils import pretty_title
from .quantity_widget import QuantityWidget


class QuantityForm(QGroupBox):
    """Form layout to dynamically generate quantity widgets and retrieve values.

    This class creates a form inside a QGroupBox with the provided fields,
    where each field is a quantity input with a nominal value, optional standard
    deviation, and unit selection. The layout is created based on the field
    configurations provided. The form's title is set as the title of the QGroupBox.

    Args:
        ureg (pint.UnitRegistry): The Pint unit registry.
        fields (list): A list of dictionaries with the fields' configuration.
                       Each dictionary contains the keys: 'label', 'unit', and
                       'std'.
        title (str): Title for the form. This is used to set the title of the
                     `QGroupBox`. Defaults to an empty string.
        pretty (bool): If True, replace "_" in labels with " " and convert to title case.

    Example:
        fields = [
            {'label': 'mass', 'unit': 'kg'},
            {'label': 'length', 'unit': 'm', 'std': False}
        ]
        form = QuantityForm(fields, title="Measurement Form", pretty=True)
    """

    def __init__(
        self,
        ureg: pint.UnitRegistry,
        fields: List[Dict[str, Union[str, bool]]],
        title: str = "",
        pretty: bool = True,
        parent: QWidget | None = None,
    ):
        super().__init__(parent)

        self.setTitle(title)
        self._field_widgets: Dict[str, "QuantityWidget"] = {}
        self._ureg = ureg
        self.pretty = pretty

        form_layout = QFormLayout()

        for field in fields:
            label = field.get("label")
            unit = field.get("unit")
            std = field.get("std", True)
            self.add_quantity_field(form_layout, label, unit, std)

        self.setLayout(form_layout)

    def _transform_label(self, label: str) -> str:
        """Transform the label shown in the form based on the pretty flag."""
        if self.pretty:
            return pretty_title(label)
        return label

    @property
    def labels(self) -> Set[str]:
        """Set of field labels."""
        return set(self._field_widgets.keys())

    def add_quantity_field(
        self, form_layout: QFormLayout, label: str, unit: str, std: bool = True
    ) -> None:
        """Add a quantity input field with a unit selector into the form."""
        qw = QuantityWidget(self._ureg, unit, std)
        form_layout.addRow(self._transform_label(label), qw.get_layout())

        # Save reference to widget to later retrieve the quantity
        self._field_widgets[label] = qw

    def get_quantities(self) -> Dict[str, Union[pint.Quantity, pint.Measurement]]:
        """Retrieve all quantities from the form."""
        return {label: self.get_quantity(label) for label in self.labels}

    def get_quantity(
        self, label: str
    ) -> Union[Union[pint.Quantity, pint.Measurement], None]:
        """Retrieve a specific quantity from the form."""
        return self._field_widgets[label].get_quantity()

    def set_quantities(
        self, values: Dict[str, Union[pint.Quantity, pint.Measurement]]
    ) -> None:
        """Set the provided quantities to the form."""
        for label, value in values.items():
            qw = self._field_widgets.get(label)
            if not qw:
                continue
            qw.set_quantity(value)
