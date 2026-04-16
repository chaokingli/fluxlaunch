"""
TurboQuant configuration panel for llama-server GUI
Specialized panel for KV cache quantization parameters with intelligent defaults
"""

import customtkinter as ctk
from typing import Optional, Callable

from .collapsible_frame import CollapsibleFrame
from .param_widgets import ParamWidgets
from .params_db import get_params_by_category, ParamCategory


class TurboQuantPanel(CollapsibleFrame):
    """
    Dedicated configuration panel for TurboQuant KV cache quantization parameters.

    Features:
    - Informational label explaining TurboQuant technology
    - Intelligent parameter selection based on VRAM recommendations
    - Integration with param_widgets for consistent UI
    - Collapsible design to save space when not needed

    The panel provides safe defaults and recommendations based on research findings:
    - K (keys) compression is sensitive - recommend q8_0 for safety
    - V (values) compression has minimal impact - recommend turbo4
    - Asymmetric configurations are generally safer than symmetric
    """

    def __init__(
        self,
        master: any,
        initial_vram_gb: int = 16,
        on_config_change: Optional[Callable[[str, any], None]] = None,
        **kwargs,
    ):
        """
        Initialize the TurboQuantPanel.

        Args:
            master: Parent widget
            initial_vram_gb: Initial VRAM size in GB for default recommendations
            on_config_change: Optional callback when any parameter changes (param_name, value)
            **kwargs: Additional arguments passed to CollapsibleFrame
        """
        # Set default title and expanded state
        kwargs.setdefault("title", "TurboQuant KV 缓存量化")
        kwargs.setdefault("expanded", False)

        super().__init__(master, **kwargs)

        self._on_config_change = on_config_change
        self._vram_gb = initial_vram_gb

        # Create parameter widgets factory
        self._param_widgets = ParamWidgets(
            self.content_frame, on_value_change=self._on_param_change
        )

        # Create the panel content
        self._create_content()

    def _create_content(self):
        """Create the panel content including info label and parameter widgets."""
        # Informational label about TurboQuant
        info_text = (
            "TurboQuant 是一种极端的 KV 缓存量化技术，可显著减少内存占用：\n"
            "• turbo3: 3.25 bits/值 (4.9x 压缩)\n"
            "• turbo4: 4.25 bits/值 (3.8x 压缩)\n\n"
            "推荐配置（基于 VRAM 大小）：\n"
            "• 安全默认值: K=q8_0, V=turbo4\n"
            "• 极端压缩: K=q8_0, V=turbo3\n"
            "• 注意: 对称 turbo3/turbo3 可能导致某些模型质量严重下降"
        )

        info_label = ctk.CTkLabel(
            self.content_frame, text=info_text, justify="left", wraplength=400
        )
        info_label.pack(padx=10, pady=(5, 10), anchor="w")

        # Get TurboQuant parameters from params_db
        turboquant_params = get_params_by_category(ParamCategory.TURBOQUANT)

        # Filter to only show relevant parameters
        relevant_params = []
        for param in turboquant_params:
            if param.name in ["cache_type_k", "cache_type_v"]:
                relevant_params.append(param)

        # Create parameter widgets
        self._widget_map = {}
        for i, param in enumerate(relevant_params):
            frame, widget = self._param_widgets.create_widget(
                param, row=i, label_width=200, widget_width=150
            )
            frame.pack(fill="x", padx=10, pady=3)
            self._widget_map[param.name] = widget

        # Add VRAM-based recommendation selector
        self._create_vram_selector()

        # Apply initial recommendations
        self._apply_vram_recommendations()

    def _create_vram_selector(self):
        """Create VRAM selector for intelligent defaults."""
        vram_frame = ctk.CTkFrame(self.content_frame, fg_color="transparent")
        vram_frame.pack(fill="x", padx=10, pady=5)

        ctk.CTkLabel(vram_frame, text="VRAM 大小:", width=200, anchor="w").pack(
            side="left"
        )

        self._vram_var = ctk.StringVar(value=str(self._vram_gb))
        vram_options = ["8", "12", "16", "24", "48", "96", "128"]

        vram_combo = ctk.CTkComboBox(
            vram_frame,
            variable=self._vram_var,
            values=vram_options,
            width=100,
            state="readonly",
            command=self._on_vram_change,
        )
        vram_combo.pack(side="left", padx=5)

        ctk.CTkButton(
            vram_frame,
            text="应用推荐",
            width=80,
            command=self._apply_vram_recommendations,
        ).pack(side="left", padx=5)

    def _on_vram_change(self, choice: str):
        """Handle VRAM selection change."""
        try:
            self._vram_gb = int(choice)
        except ValueError:
            pass

    def _apply_vram_recommendations(self):
        """Apply VRAM-based recommendations to parameter widgets."""
        # Get current model info (would be passed in real implementation)
        # For now, use safe defaults based on VRAM

        if self._vram_gb <= 8:
            # Extreme compression for low VRAM
            k_type = "q8_0"
            v_type = "turbo2"
        elif self._vram_gb <= 12:
            # Safe asymmetric for moderate VRAM
            k_type = "q8_0"
            v_type = "turbo3"
        elif self._vram_gb <= 16:
            # Best quality TurboQuant for decent VRAM
            k_type = "turbo4"
            v_type = "turbo4"
        elif self._vram_gb <= 24:
            # Mixed approach for larger VRAM
            k_type = "q8_0"
            v_type = "turbo3"
        else:
            # High quality for ample VRAM
            k_type = "turbo4"
            v_type = "turbo4"

        # Set the values in widgets
        if "cache_type_k" in self._widget_map:
            self._widget_map["cache_type_k"].set_value(k_type)
        if "cache_type_v" in self._widget_map:
            self._widget_map["cache_type_v"].set_value(v_type)

    def _on_param_change(self, param_name: str, value: any):
        """Handle parameter value changes."""
        if self._on_config_change:
            self._on_config_change(param_name, value)

    def get_config(self) -> dict[str, any]:
        """
        Get current TurboQuant configuration.

        Returns:
            Dictionary with current parameter values
        """
        return self._param_widgets.get_all_values()

    def set_config(self, config: dict[str, any]):
        """
        Set TurboQuant configuration from dictionary.

        Args:
            config: Dictionary with parameter values
        """
        self._param_widgets.set_all_values(config)

        # Update VRAM selector if config contains relevant info
        # (This would be extended in full implementation)

    def get_recommended_config(self, vram_gb: int) -> dict[str, str]:
        """
        Get recommended configuration based on VRAM size.

        Args:
            vram_gb: VRAM size in GB

        Returns:
            Recommended configuration dictionary
        """
        if vram_gb <= 8:
            return {"cache_type_k": "q8_0", "cache_type_v": "turbo2"}
        elif vram_gb <= 12:
            return {"cache_type_k": "q8_0", "cache_type_v": "turbo3"}
        elif vram_gb <= 16:
            return {"cache_type_k": "turbo4", "cache_type_v": "turbo4"}
        elif vram_gb <= 24:
            return {"cache_type_k": "q8_0", "cache_type_v": "turbo3"}
        else:
            return {"cache_type_k": "turbo4", "cache_type_v": "turbo4"}


if __name__ == "__main__":
    # Simple test to verify the panel can be created
    root = ctk.CTk()
    root.title("TurboQuant Panel Test")
    root.geometry("600x400")

    panel = TurboQuantPanel(root, initial_vram_gb=16)
    panel.pack(fill="x", padx=10, pady=10)

    def print_config():
        config = panel.get_config()
        print("Current config:", config)

    btn = ctk.CTkButton(root, text="Print Config", command=print_config)
    btn.pack(pady=10)

    root.mainloop()
