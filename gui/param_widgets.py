"""
Parameter widgets generator for llama-server GUI
Creates CustomTkinter input controls based on parameter definitions.
"""

import customtkinter as ctk
from typing import Any, Callable, Optional, Union

from .params_db import ParamDef, UIType


class ParamWidget:
    """
    Wrapper class for parameter input controls.
    Provides unified get_value() and set_value() interfaces.
    """

    def __init__(
        self,
        widget: ctk.CTkBaseClass,
        widget_type: str,
        param_def: ParamDef,
        parent: ctk.CTkBaseClass,
    ):
        """
        Initialize parameter widget wrapper.

        Args:
            widget: The actual CustomTkinter widget instance
            widget_type: Type of widget ('entry', 'spinbox', 'checkbox', 'combobox', 'slider')
            param_def: Parameter definition for this widget
            parent: Parent container for additional UI elements (like slider label)
        """
        self.widget = widget
        self.widget_type = widget_type
        self.param_def = param_def
        self.parent = parent
        self._value_var = None

        # Set up value variable based on widget type
        if widget_type == "checkbox":
            self._value_var = widget.cget("variable")
        elif widget_type == "combobox":
            self._value_var = widget.cget("variable")
        elif widget_type == "slider":
            # Slider uses a separate StringVar for display
            self._value_var = (
                widget.cget("variable") if hasattr(widget, "cget") else None
            )

    def get_value(self) -> Any:
        """
        Get current value from widget, converted to parameter type.

        Returns:
            Value in the correct type (int, float, str, bool)
        """
        if self.widget_type == "checkbox":
            return self.widget.get()

        elif self.widget_type == "slider":
            # Slider value is stored in textvariable
            if self._value_var:
                return self._value_var.get()
            return self.widget.get()

        elif self.widget_type == "combobox":
            return self.widget.get()

        else:  # entry/spinbox
            value = self.widget.get()
            return self._convert_value(value)

    def set_value(self, value: Any) -> None:
        """
        Set value to widget from parameter value.

        Args:
            value: Value to set (will be converted to string for UI)
        """
        if self.widget_type == "checkbox":
            self.widget.select() if value else self.widget.deselect()

        elif self.widget_type == "slider":
            if self._value_var:
                self._value_var.set(str(value))
            self.widget.set(value)

        elif self.widget_type == "combobox":
            # CTkComboBox uses set() instead of delete/insert
            self.widget.set(str(value) if value is not None else "")

        else:  # entry/spinbox
            self.widget.delete(0, "end")
            self.widget.insert(0, str(value) if value is not None else "")

    def _convert_value(self, value: str) -> Any:
        """
        Convert string value to parameter type.

        Args:
            value: String value from widget

        Returns:
            Value converted to parameter type
        """
        param_type = self.param_def.param_type

        # Handle empty string
        if not value or value == "":
            if param_type == str:
                return ""
            elif param_type == bool:
                return False
            elif param_type in (int, float):
                return None if self.param_def.default is None else param_type(0)
            return None

        try:
            if param_type == bool:
                # Handle boolean string conversion
                if isinstance(value, bool):
                    return value
                return value.lower() in ("true", "1", "yes")

            elif param_type == int:
                return int(value)

            elif param_type == float:
                return float(value)

            else:  # str or other types
                return str(value)

        except (ValueError, TypeError):
            return None

    def validate(self) -> bool:
        """
        Validate current widget value against parameter constraints.

        Returns:
            True if value is valid, False otherwise
        """
        value = self.get_value()

        if value is None or value == "":
            return True  # Empty values allowed for optional params

        # Type validation
        if not isinstance(value, self.param_def.param_type):
            try:
                converted = self.param_def.param_type(value)
                if self.param_def.param_type == bool and isinstance(value, str):
                    if value.lower() not in ("true", "false", "1", "0", ""):
                        return False
            except (ValueError, TypeError):
                return False

        # Range validation for numeric types
        if self.param_def.param_type in (int, float) and isinstance(
            value, (int, float)
        ):
            if self.param_def.min_val is not None and value < self.param_def.min_val:
                return False
            if self.param_def.max_val is not None and value > self.param_def.max_val:
                return False

        # Choices validation
        if self.param_def.choices is not None:
            if value not in self.param_def.choices:
                return False

        return True


class ParamWidgets:
    """
    Factory class for creating parameter input widgets.
    Generates appropriate CustomTkinter controls based on UIType.
    """

    def __init__(
        self,
        parent: ctk.CTkBaseClass,
        on_value_change: Optional[Callable[[str, Any], None]] = None,
    ):
        """
        Initialize ParamWidgets factory.

        Args:
            parent: Parent container for widgets
            on_value_change: Optional callback when value changes (param_name, value)
        """
        self.parent = parent
        self.on_value_change = on_value_change
        self._widgets: dict[str, ParamWidget] = {}

    def create_widget(
        self,
        param_def: ParamDef,
        row: int,
        column: int = 0,
        label_width: int = 180,
        widget_width: int = 200,
    ) -> tuple[ctk.CTkFrame, ParamWidget]:
        """
        Create a widget for a parameter definition.

        Args:
            param_def: Parameter definition to create widget for
            row: Grid row position
            column: Grid column position (0 for label column)
            label_width: Width of label in pixels
            widget_width: Width of input widget in pixels

        Returns:
            Tuple of (frame, param_widget) where frame contains the widget
        """
        # Create container frame
        frame = ctk.CTkFrame(self.parent, fg_color="transparent")
        frame.pack(fill="x", padx=5, pady=3)

        label_width = 150  # Fixed width for consistent layout
        friendly_name = param_def.name.replace("_", " ").title()
        label = ctk.CTkLabel(frame, text=friendly_name, width=label_width, anchor="w")
        label.pack(side="left", padx=(0, 10))

        # Create appropriate widget based on UIType
        param_widget = self._create_widget_instance(param_def, frame, widget_width)

        # Store widget reference
        self._widgets[param_def.name] = param_widget

        return frame, param_widget

    def _create_widget_instance(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass, width: int
    ) -> ParamWidget:
        """
        Create the actual widget instance based on UIType.

        Args:
            param_def: Parameter definition
            parent: Parent container
            width: Widget width

        Returns:
            ParamWidget wrapper
        """
        ui_type = param_def.ui_type

        if ui_type == UIType.ENTRY:
            return self._create_entry_widget(param_def, parent, width)

        elif ui_type == UIType.SPINBOX:
            return self._create_spinbox_widget(param_def, parent, width)

        elif ui_type == UIType.CHECKBOX:
            return self._create_checkbox_widget(param_def, parent)

        elif ui_type == UIType.COMBOBOX:
            return self._create_combobox_widget(param_def, parent, width)

        elif ui_type == UIType.SLIDER:
            return self._create_slider_widget(param_def, parent, width)

        else:
            # Fallback to entry for unknown types
            return self._create_entry_widget(param_def, parent, width)

    def _create_entry_widget(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass, width: int
    ) -> ParamWidget:
        """Create text entry widget."""
        var = ctk.StringVar(
            value=str(param_def.default) if param_def.default is not None else ""
        )

        if param_def.param_type == bool:
            # For boolean types, use_combobox with True/False options
            widget = ctk.CTkComboBox(
                parent,
                variable=var,
                values=["True", "False"],
                width=width,
                state="readonly",
            )
            widget.pack(side="right", padx=5)
            return ParamWidget(widget, "entry", param_def, parent)

        widget = ctk.CTkEntry(parent, textvariable=var, width=width)
        widget.pack(side="right", padx=5)
        return ParamWidget(widget, "entry", param_def, parent)

    def _create_spinbox_widget(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass, width: int
    ) -> ParamWidget:
        """
        Create numeric input with validation.
        Uses CTkEntry with validation callbacks.
        """
        var = ctk.StringVar(
            value=str(param_def.default) if param_def.default is not None else ""
        )

        # Validation callbacks
        def validate_numeric(new_value: str) -> bool:
            """Validate numeric input."""
            if not new_value:  # Empty is allowed (for Optional params)
                return True
            try:
                if param_def.param_type == int:
                    int(new_value)
                elif param_def.param_type == float:
                    float(new_value)
                return True
            except ValueError:
                return False

        def on_validate(p) -> bool:
            """Wrapper for tkinter validation."""
            return validate_numeric(p)

        widget = ctk.CTkEntry(
            parent,
            textvariable=var,
            width=width,
            validate="key",
            validatecommand=(parent.register(on_validate), "%P"),
        )
        widget.pack(side="right", padx=5)

        return ParamWidget(widget, "spinbox", param_def, parent)

    def _create_checkbox_widget(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass
    ) -> ParamWidget:
        """Create checkbox toggle widget."""
        var = ctk.BooleanVar(
            value=bool(param_def.default) if param_def.default is not None else False
        )
        widget = ctk.CTkCheckBox(parent, variable=var, text="")
        widget.pack(side="right", padx=5)
        return ParamWidget(widget, "checkbox", param_def, parent)

    def _create_combobox_widget(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass, width: int
    ) -> ParamWidget:
        """Create dropdown combobox widget."""
        var = ctk.StringVar(
            value=str(param_def.default)
            if param_def.default in (param_def.choices or [])
            else (param_def.choices[0] if param_def.choices else "")
        )

        widget = ctk.CTkComboBox(
            parent,
            variable=var,
            values=param_def.choices or [],
            width=width,
            state="readonly",
        )
        widget.pack(side="right", padx=5)
        return ParamWidget(widget, "combobox", param_def, parent)

    def _create_slider_widget(
        self, param_def: ParamDef, parent: ctk.CTkBaseClass, width: int
    ) -> ParamWidget:
        """
        Create slider with value display label.
        Slider controls the value, label shows current value.
        """
        # Create frame for slider and label
        slider_frame = ctk.CTkFrame(parent, fg_color="transparent")
        slider_frame.pack(fill="x", padx=5, pady=2)

        # Slider value display label
        default_val = param_def.default if param_def.default is not None else 0

        # Determine slider range
        min_val = getattr(param_def, "min_val", 0) or 0
        max_val = getattr(param_def, "max_val", 100) or 100

        # For float params, scale slider and display formatted value
        if param_def.param_type == float:
            # Use integer slider with scaled display
            scale = 100  # 2 decimal places
            int_default = int(default_val * scale)
            int_min = int(min_val * scale)
            int_max = int(max_val * scale)

            slider_var = ctk.DoubleVar(value=int_default)
            slider = ctk.CTkSlider(
                slider_frame,
                from_=int_min,
                to=int_max,
                variable=slider_var,
                width=width,
            )
            slider.pack(side="left", fill="x", expand=True)

            # Label to show formatted value
            label_var = ctk.StringVar(value=f"{default_val:.2f}")
            label = ctk.CTkLabel(
                slider_frame, textvariable=label_var, width=60, anchor="e"
            )
            label.pack(side="right", padx=(10, 0))

            # Update label when slider changes
            def update_label(*args):
                val = slider_var.get() / scale
                label_var.set(f"{val:.2f}")

            slider_var.trace_add("write", update_label)

        else:  # int
            slider_var = ctk.DoubleVar(value=default_val)
            slider = ctk.CTkSlider(
                slider_frame,
                from_=min_val,
                to=max_val,
                variable=slider_var,
                width=width,
            )
            slider.pack(side="left", fill="x", expand=True)

            # Label to show value
            label_var = ctk.StringVar(value=str(default_val))
            label = ctk.CTkLabel(
                slider_frame, textvariable=label_var, width=60, anchor="e"
            )
            label.pack(side="right", padx=(10, 0))

            # Update label when slider changes
            def update_label(*args):
                val = int(slider_var.get())
                label_var.set(str(val))

            slider_var.trace_add("write", update_label)

        return ParamWidget(slider, "slider", param_def, slider_frame)

    def get_widget(self, param_name: str) -> Optional[ParamWidget]:
        """
        Get widget by parameter name.

        Args:
            param_name: Name of parameter

        Returns:
            ParamWidget or None if not found
        """
        return self._widgets.get(param_name)

    def get_all_values(self) -> dict[str, Any]:
        """
        Get values from all widgets.

        Returns:
            Dictionary of param_name -> value
        """
        return {name: widget.get_value() for name, widget in self._widgets.items()}

    def set_all_values(self, values: dict[str, Any]) -> None:
        """
        Set values for all widgets.

        Args:
            values: Dictionary of param_name -> value
        """
        for name, value in values.items():
            if name in self._widgets:
                self._widgets[name].set_value(value)

    def clear_widgets(self) -> None:
        """Remove all created widgets from parent."""
        for widget in self._widgets.values():
            if hasattr(widget.parent, "destroy"):
                widget.parent.destroy()
        self._widgets.clear()
